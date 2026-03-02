#!/usr/bin/env python3
"""
DevOps-MAS Quick Start
Standalone launcher that works without any internal platform dependencies.
Supports: CLI interactive mode, API server, and Web GUI.
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def setup_demo_data():
    """Generate demo data if not exists."""
    cases_dir = PROJECT_ROOT / "data" / "test" / "cases"
    if not list(cases_dir.glob("OC-*.json")):
        print("Generating demo data...")
        from data.test.demo_data import generate_all
        generate_all()
    else:
        print(f"Demo data already exists ({len(list(cases_dir.glob('OC-*.json')))} cases)")


def run_cli(args):
    """Interactive CLI mode."""
    from llm.api_provider import APIModelProvider
    from agents.memory import AgentMemory
    from cases.tracker import CaseTracker

    config = _load_config()
    llm = APIModelProvider(config.get("api_llm", {}))
    memory = AgentMemory(memory_dir=str(PROJECT_ROOT / "data" / "memory"))
    tracker = CaseTracker(storage_dir=str(PROJECT_ROOT / "data" / "test" / "cases"))

    print("\n" + "=" * 60)
    print("  🛡️  DevOps-MAS - Interactive CLI")
    print("  Type your question, or use commands:")
    print("    /cases     - List recent cases")
    print("    /stats     - Show system stats")
    print("    /clear     - Clear conversation")
    print("    /quit      - Exit")
    print("=" * 60 + "\n")

    while True:
        try:
            query = input("You > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not query:
            continue
        if query == "/quit":
            print("Goodbye!")
            break
        if query == "/cases":
            cases = tracker.list_cases(limit=5)
            for c in cases:
                print(f"  [{c.priority.value}] {c.case_id}: {c.title} ({c.status.value})")
            continue
        if query == "/stats":
            print(f"  Memory: {memory.get_stats()}")
            print(f"  Cases: {tracker.get_stats()}")
            continue
        if query == "/clear":
            memory.clear_session()
            print("  Conversation cleared.")
            continue

        memory.add_message("user", query)
        history = memory.get_context_window(max_tokens_estimate=3000)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are DevOps-MAS, an expert multi-agent DevOps assistant. "
                    "Analyze issues systematically, provide diagnostics and actionable solutions."
                ),
            }
        ]
        messages.extend(history[-6:])
        messages.append({"role": "user", "content": query})

        print("\n🤔 Analyzing...\n")
        try:
            resp = asyncio.run(llm.generate(messages, max_tokens=1024, temperature=0.3))
            if resp.success:
                print(f"DevOps-MAS > {resp.content}\n")
                print(f"  [Model: {resp.model} | Latency: {resp.latency_ms:.0f}ms | Tokens: {resp.usage.get('total_tokens', '?')}]\n")
                memory.add_message("assistant", resp.content)
            else:
                print(f"⚠️ Error: {resp.error}\n")
        except Exception as e:
            print(f"⚠️ Error: {e}\n")
            print("Make sure OPENAI_API_KEY is set or configure in config.json\n")

    asyncio.run(llm.close())


def run_gui(args):
    """Launch Streamlit Web GUI."""
    import subprocess
    app_path = PROJECT_ROOT / "web" / "streamlit_app.py"
    port = args.port or 8501
    print(f"\n🚀 Launching DevOps-MAS GUI on http://localhost:{port}\n")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", str(app_path),
        "--server.port", str(port),
        "--server.headless", "true",
        "--theme.primaryColor", "#667eea",
    ])


def run_api(args):
    """Launch FastAPI server."""
    import uvicorn
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    from typing import Optional

    config = _load_config()
    llm_provider = APIModelProvider(config.get("api_llm", {}))
    memory = AgentMemory(memory_dir=str(PROJECT_ROOT / "data" / "memory"))
    tracker = CaseTracker(storage_dir=str(PROJECT_ROOT / "data" / "test" / "cases"))

    app = FastAPI(title="DevOps-MAS API", version="2.0.0")

    class QueryRequest(BaseModel):
        query: str
        image: Optional[str] = None
        case_id: Optional[str] = None
        model: Optional[str] = None

    class QueryResponse(BaseModel):
        answer: str
        confidence: float
        model: str
        latency_ms: float

    @app.post("/api/query", response_model=QueryResponse)
    async def query(req: QueryRequest):
        messages = [
            {"role": "system", "content": "You are DevOps-MAS, an expert DevOps assistant."},
            {"role": "user", "content": req.query},
        ]
        resp = await llm_provider.generate(messages, model=req.model, image=req.image)
        if not resp.success:
            raise HTTPException(500, resp.error)
        return QueryResponse(
            answer=resp.content,
            confidence=0.85,
            model=resp.model,
            latency_ms=resp.latency_ms,
        )

    @app.get("/api/cases")
    async def list_cases():
        return [c.to_dict() for c in tracker.list_cases(limit=50)]

    @app.get("/api/stats")
    async def stats():
        return {
            "memory": memory.get_stats(),
            "cases": tracker.get_stats(),
        }

    @app.get("/health")
    async def health():
        return {"status": "ok", "version": "2.0.0"}

    port = args.port or 8000
    print(f"\n🚀 DevOps-MAS API server starting on http://localhost:{port}")
    print(f"📖 API docs at http://localhost:{port}/docs\n")
    uvicorn.run(app, host="0.0.0.0", port=port)


def _load_config():
    config_path = PROJECT_ROOT / "config.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}


def main():
    parser = argparse.ArgumentParser(description="DevOps-MAS - Multi-Agent DevOps System")
    sub = parser.add_subparsers(dest="command", help="Run mode")

    cli_parser = sub.add_parser("cli", help="Interactive CLI mode")
    gui_parser = sub.add_parser("gui", help="Web GUI mode (Streamlit)")
    gui_parser.add_argument("--port", type=int, default=8501)
    api_parser = sub.add_parser("api", help="REST API server mode")
    api_parser.add_argument("--port", type=int, default=8000)
    sub.add_parser("demo", help="Generate demo data")

    args = parser.parse_args()

    if args.command == "cli":
        setup_demo_data()
        run_cli(args)
    elif args.command == "gui":
        setup_demo_data()
        run_gui(args)
    elif args.command == "api":
        setup_demo_data()
        run_api(args)
    elif args.command == "demo":
        setup_demo_data()
    else:
        parser.print_help()
        print("\nExamples:")
        print("  python quickstart.py cli        # Interactive CLI")
        print("  python quickstart.py gui        # Web GUI (default: port 8501)")
        print("  python quickstart.py api        # REST API (default: port 8000)")
        print("  python quickstart.py demo       # Generate demo data")


if __name__ == "__main__":
    main()
