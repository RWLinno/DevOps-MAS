#!/usr/bin/env python3
"""
Unified Server for DevOps-MAS
Serves both the React Demo frontend and the real API backend.

Usage:
    python server_unified.py
    # Demo UI:  http://localhost:8000
    # API docs: http://localhost:8000/docs
    # Streamlit: launch separately with `python quickstart.py gui`
"""

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from llm.api_provider import APIModelProvider
from agents.memory import AgentMemory, EpisodicMemory
from cases.tracker import CaseTracker, CaseStatus
from cases.analyzer import CaseAnalyzer
from sft.data_collector import SFTDataCollector
from tools.mcp_toolkit import MCPToolkit

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Load Config ──
def load_config() -> dict:
    config_path = PROJECT_ROOT / "config.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}

config = load_config()

# ── Init Services ──
llm = APIModelProvider(config.get("api_llm", {}))
memory = AgentMemory(memory_dir=str(PROJECT_ROOT / "data" / "memory"))
tracker = CaseTracker(storage_dir=str(PROJECT_ROOT / "data" / "test" / "cases"))
analyzer = CaseAnalyzer(tracker)
sft_collector = SFTDataCollector(data_dir=str(PROJECT_ROOT / "data" / "sft"))
mcp_toolkit = MCPToolkit(config.get("mcp", {}))

# ── App ──
app = FastAPI(
    title="DevOps-MAS API",
    description="Multi-Agent Intelligent DevOps System",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request/Response Models ──

class ChatRequest(BaseModel):
    query: str
    image: Optional[str] = None
    case_id: Optional[str] = None
    model: Optional[str] = None
    symbols: Optional[List[str]] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    confidence: float
    model: str
    latency_ms: float
    agent_used: str
    tokens_used: Optional[int] = None
    similar_cases: Optional[List[dict]] = None

class CaseCreateRequest(BaseModel):
    title: str
    description: str
    priority: str = "P2"
    tags: List[str] = []

class ToolCallRequest(BaseModel):
    tool_name: str
    params: Dict[str, Any] = {}

# ── Chat API ──

@app.get("/api/chat")
async def chat_info():
    """Usage info for the chat endpoint."""
    return {
        "endpoint": "POST /api/chat",
        "description": "Send a query to the multi-agent system",
        "request_body": {
            "query": "(required) string — your question",
            "image": "(optional) base64 image string",
            "case_id": "(optional) link to an existing case",
            "model": "(optional) override default LLM model",
            "symbols": "(optional) list of command symbols like @, /debug, /monitor",
            "session_id": "(optional) session identifier for context",
        },
        "example": {
            "query": "Redis连接超时如何排查？",
            "symbols": ["/debug"],
        },
        "docs": "/docs#/default/chat_api_chat_post",
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Process a user query through the multi-agent system."""
    start = time.time()

    memory.add_message("user", req.query, case_id=req.case_id)
    history = memory.get_context_window(max_tokens_estimate=3000)
    similar = memory.search_episodes(req.query, top_k=2)

    case_context = ""
    similar_cases_data = []
    if similar:
        for ep in similar:
            case_context += f"\n[Past Case: {ep.title}] Root Cause: {ep.root_cause} | Solution: {ep.solution}"
            similar_cases_data.append({
                "case_id": ep.case_id,
                "title": ep.title,
                "root_cause": ep.root_cause,
                "solution": ep.solution[:200],
            })

    agent_hint = _detect_agent_from_symbols(req.symbols or [], req.query)

    system_prompt = (
        "You are DevOps-MAS, an expert multi-agent DevOps assistant. "
        "You have specialized agents for: log analysis, metrics analysis, visual analysis, "
        "knowledge retrieval (RAG), web search, and comprehensive reasoning. "
        "Analyze the user's issue systematically and provide actionable solutions. "
        "Use structured markdown formatting with clear sections."
    )
    if case_context:
        system_prompt += f"\n\nRelevant past cases:\n{case_context}"
    if agent_hint:
        system_prompt += f"\n\nActivated agent: {agent_hint}"

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history[-6:])
    messages.append({"role": "user", "content": req.query})

    resp = await llm.generate(
        messages,
        model=req.model,
        image=req.image,
        max_tokens=2048,
        temperature=0.3,
    )

    if not resp.success:
        raise HTTPException(500, f"LLM error: {resp.error}")

    memory.add_message("assistant", resp.content, agent_name=agent_hint or "comprehensive_agent")

    sft_collector.collect_from_interaction(
        req.query, resp.content, 0.85, agent_hint or "comprehensive_agent"
    )

    if req.case_id:
        try:
            tracker.add_message(req.case_id, f"Q: {req.query}\nA: {resp.content[:300]}...", agent_name="chat")
        except Exception:
            pass

    return ChatResponse(
        answer=resp.content,
        confidence=0.85,
        model=resp.model,
        latency_ms=(time.time() - start) * 1000,
        agent_used=agent_hint or "comprehensive_agent",
        tokens_used=resp.usage.get("total_tokens"),
        similar_cases=similar_cases_data if similar_cases_data else None,
    )


def _detect_agent_from_symbols(symbols: List[str], query: str) -> Optional[str]:
    if "/debug" in symbols or "/debug" in query:
        return "log_analysis_agent"
    if "/monitor" in symbols or "/monitor" in query:
        return "metrics_analysis_agent"
    if "/visual" in symbols or "/visual" in query:
        return "visual_analysis_agent"
    if "/search" in symbols or "/search" in query:
        return "search_agent"
    if "@" in query:
        return "retriever_agent"
    if "!urgent" in symbols or "!urgent" in query:
        return "comprehensive_agent"
    return None


# ── Cases API ──

@app.get("/api/cases")
async def list_cases(status: Optional[str] = None, limit: int = 50):
    s = CaseStatus(status) if status else None
    cases = tracker.list_cases(status=s, limit=limit)
    return [c.to_dict() for c in cases]

@app.get("/api/cases/{case_id}")
async def get_case(case_id: str):
    case = tracker.get_case(case_id)
    if not case:
        raise HTTPException(404, "Case not found")
    return case.to_dict()

@app.post("/api/cases")
async def create_case(req: CaseCreateRequest):
    case = tracker.create_case(req.title, req.description, req.priority, req.tags)
    return case.to_dict()

@app.get("/api/cases/stats/overview")
async def case_stats():
    return tracker.get_stats()

@app.get("/api/analytics/report")
async def analytics_report():
    report = analyzer.generate_report()
    return {
        "summary": report.summary,
        "total_cases": report.total_cases,
        "resolved_cases": report.resolved_cases,
        "avg_resolution_time_min": report.avg_resolution_time_min,
        "top_tags": report.top_tags,
        "priority_distribution": report.priority_distribution,
        "status_distribution": report.status_distribution,
        "recommendations": report.recommendations,
    }

@app.get("/api/analytics/visualization")
async def analytics_viz():
    return analyzer.get_visualization_data()

# ── Tools API (MCP) ──

@app.get("/api/tools")
async def list_tools():
    return mcp_toolkit.get_available_tools()

@app.post("/api/tools/execute")
async def execute_tool(req: ToolCallRequest):
    result = await mcp_toolkit.execute_tool(req.tool_name, req.params)
    return result

# ── Memory API ──

@app.get("/api/memory/stats")
async def memory_stats():
    return memory.get_stats()

@app.get("/api/memory/episodes")
async def list_episodes():
    from dataclasses import asdict
    return [asdict(ep) for ep in memory.get_all_episodes()]

# ── SFT API ──

@app.get("/api/sft/stats")
async def sft_stats():
    return sft_collector.get_stats()

@app.post("/api/sft/export/{format}")
async def sft_export(format: str):
    path = sft_collector.export_to_file(format)
    return {"path": path, "format": format}

# ── System API ──

@app.get("/api/system/status")
async def system_status():
    return {
        "status": "online",
        "version": "2.0.0",
        "agents": {
            "route_agent": {"status": "active"},
            "log_analysis_agent": {"status": "active"},
            "metrics_analysis_agent": {"status": "active"},
            "visual_analysis_agent": {"status": "active"},
            "knowledge_agent": {"status": "active"},
            "retriever_agent": {"status": "active"},
            "search_agent": {"status": "active"},
            "comprehensive_agent": {"status": "active"},
        },
        "memory": memory.get_stats(),
        "cases": tracker.get_stats(),
        "sft": sft_collector.get_stats(),
    }

@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}


# ── Serve Demo Frontend ──

DEMO_DIST = PROJECT_ROOT / "demo" / "dist"

if DEMO_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(DEMO_DIST / "assets")), name="demo-assets")

    @app.get("/favicon.ico")
    async def favicon():
        ico = DEMO_DIST / "favicon.ico"
        if ico.exists():
            return FileResponse(str(ico), media_type="image/x-icon")
        raise HTTPException(404)

    @app.get("/demo")
    async def demo_page():
        return FileResponse(str(DEMO_DIST / "index.html"))

    @app.get("/demo/{path:path}")
    async def demo_files(path: str):
        file_path = DEMO_DIST / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(DEMO_DIST / "index.html"))

    logger.info(f"Demo frontend mounted at /demo from {DEMO_DIST}")


# ── Root redirect ──

@app.get("/")
async def root():
    """Root page with links to all interfaces."""
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>DevOps-MAS</title>
        <style>
            body {{ font-family: 'Inter', -apple-system, sans-serif; max-width: 800px; margin: 60px auto; padding: 0 20px; background: #f8f9fa; }}
            h1 {{ color: #1a1a2e; font-size: 2rem; }}
            .card {{ background: white; border-radius: 12px; padding: 24px; margin: 16px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
            .card h3 {{ margin-top: 0; color: #333; }}
            .card a {{ color: #667eea; text-decoration: none; font-weight: 600; }}
            .card a:hover {{ text-decoration: underline; }}
            .card p {{ color: #666; margin: 4px 0; font-size: 0.9rem; }}
            .status {{ display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; background: #d4edda; color: #155724; }}
        </style>
    </head>
    <body>
        <h1>🛡️ DevOps-MAS</h1>
        <p>Multi-Agent Intelligent DevOps System <span class="status">Online v2.0</span></p>

        <div class="card">
            <h3>🎨 <a href="/demo">Interactive Demo</a></h3>
            <p>React-based interactive frontend with chat, monitoring, agent visualization</p>
        </div>

        <div class="card">
            <h3>📖 <a href="/docs">API Documentation</a></h3>
            <p>Full Swagger/OpenAPI documentation for all endpoints</p>
        </div>

        <div class="card">
            <h3>🔌 API Endpoints</h3>
            <p><code>POST /api/chat</code> — Intelligent Q&A with multi-agent support</p>
            <p><code>GET /api/cases</code> — Case management</p>
            <p><code>GET /api/analytics/report</code> — Analytics & visualization</p>
            <p><code>GET /api/tools</code> — MCP tools listing</p>
            <p><code>GET /api/system/status</code> — System health status</p>
        </div>

        <div class="card">
            <h3>🖥️ Streamlit GUI</h3>
            <p>Launch separately: <code>python quickstart.py gui</code></p>
        </div>
    </body>
    </html>
    """)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  🛡️  DevOps-MAS Unified Server v2.0")
    print("  " + "-" * 54)
    print(f"  🌐 Root:     http://localhost:8000")
    print(f"  🎨 Demo:     http://localhost:8000/demo")
    print(f"  📖 API Docs: http://localhost:8000/docs")
    print(f"  💬 Chat API: POST http://localhost:8000/api/chat")
    print("=" * 60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
