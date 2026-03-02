# DevOps-MAS

**Multi-Agent Intelligent DevOps System with Vision-Language Models**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-green.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/streamlit-1.24+-red.svg)](https://streamlit.io)

DevOps-MAS 是一个基于 Multi-Agent System 范式的智能运维问答系统，专为企业 DevOps 场景设计。通过多智能体协作、多模态理解（VLM）、检索增强生成（RAG）、工具调用（MCP/Function Calling）和数据微调（SFT）等技术，帮助工程师快速诊断和解决技术问题，显著提升工程运维效率。

> **Standalone Mode**: 支持 `pip install` + `OPENAI_API_KEY` 即可 Quick Start。

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Multi-Agent Orchestration** | Orchestrator-Worker 模式，8+ 专业智能体协同（路由、日志、指标、视觉、检索、搜索、综合分析） |
| **Agent Memory** | 三层记忆系统：短期会话（Sliding Window）、长期知识（Persistent）、情景记忆（Episodic Case History） |
| **RAG Retrieval** | 知识库检索增强生成，支持 @文档名.md 精确引用，SimpleRAG + DatabaseRAG 双引擎 |
| **MCP / Function Calling** | MCP 协议工具集成（数据库健康检查、日志分析、系统监控），支持 LLM Function Calling |
| **Multimodal VLM** | 支持 Qwen2.5-VL 本地部署 / OpenAI GPT-4o API 两种方式处理图像 |
| **Case Analytics** | 运维问题全生命周期追踪（创建 → 诊断 → 解决 → 复盘），可视化报告 & 趋势分析 |
| **SFT Studio** | 自动收集高质量 Q&A 数据，支持 Alpaca / ShareGPT 格式导出，LoRA/QLoRA 微调配置生成 |
| **Modern GUI** | Streamlit 现代化界面：智能对话、Case 管理、分析仪表盘、SFT 工作台 |
| **Platform Adapters** | 飞书、Slack 等平台适配器，支持扩展 |
| **Docker Ready** | Docker Compose 一键部署，包含 API + GUI + 数据库 |

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    User Interface Layer                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ Web GUI  │  │ REST API │  │   CLI    │  │ Feishu   │ │
│  │(Streamlit)│  │(FastAPI) │  │          │  │  Bot     │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘ │
├───────┴──────────────┴────────────┴──────────────┴───────┤
│                 Orchestrator Layer                         │
│  ┌──────────────────────────────────────────────────────┐ │
│  │              Agent Orchestrator                       │ │
│  │  Route → Execute → Synthesize → Memory Store         │ │
│  └──────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────┤
│                  Agent Layer (8 Specialists)               │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐            │
│  │ Route  │ │ Visual │ │  Log   │ │Metrics │            │
│  │ Agent  │ │Analysis│ │Analysis│ │Analysis│            │
│  └────────┘ └────────┘ └────────┘ └────────┘            │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐            │
│  │Knowledge│ │Retriever│ │ Search │ │Compre- │            │
│  │ Agent  │ │ (RAG)  │ │ Agent  │ │hensive │            │
│  └────────┘ └────────┘ └────────┘ └────────┘            │
├──────────────────────────────────────────────────────────┤
│                 Infrastructure Layer                       │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐            │
│  │  LLM   │ │  RAG   │ │  MCP   │ │ Agent  │            │
│  │Provider │ │ Engine │ │ Tools  │ │ Memory │            │
│  └────────┘ └────────┘ └────────┘ └────────┘            │
│  ┌────────┐ ┌────────┐ ┌────────┐                        │
│  │  Case  │ │  SFT   │ │Privacy │                        │
│  │Tracker │ │Collector│ │Adapter │                        │
│  └────────┘ └────────┘ └────────┘                        │
└──────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Prerequisites
- Python 3.9+
- An OpenAI API key (or any OpenAI-compatible endpoint)

### 1. Install

```bash
git clone https://github.com/rwlinno/DevOps-MAS.git
cd DevOps-MAS

conda create -n devops-mas python=3.10 && conda activate devops-mas
pip install -r requirements.txt
```

### 2. Configure

```bash
# Option A: Environment variable (simplest)
export OPENAI_API_KEY="sk-..."

# Option B: Copy and edit config
cp config.example.json config.json
# Edit api_llm.api_key in config.json
```

### 3. Run

```bash
# Generate demo data
python quickstart.py demo

# Interactive CLI
python quickstart.py cli

# Web GUI (recommended)
python quickstart.py gui

# REST API Server
python quickstart.py api
```

### 4. Unified Server (API + Demo Frontend)

```bash
python server_unified.py

# Visit:
#   http://localhost:8000       - Dashboard
#   http://localhost:8000/demo  - React Interactive Demo
#   http://localhost:8000/docs  - Swagger API docs
```

### 5. Docker (Optional)

```bash
docker-compose up -d
# GUI: http://localhost:8501
# API: http://localhost:8000/docs
```

---

## Project Structure

```
DevOps-MAS/
├── quickstart.py           # Entry point (CLI/GUI/API modes)
├── server_unified.py       # Unified FastAPI server (API + React Demo)
├── config.example.json     # Configuration template
├── requirements.txt        # Python dependencies
├── agents/                 # Multi-Agent System
│   ├── base.py            # Base agent framework
│   ├── core_agents.py     # 8 specialist agents
│   ├── enhanced_route_agent.py  # Enhanced routing with semantic analysis
│   ├── orchestrator.py    # Orchestrator-Worker coordinator
│   ├── memory.py          # 3-layer memory system
│   ├── search_agent.py    # Web search agent
│   └── unified_manager.py # Unified agent & model manager
├── llm/                    # LLM Providers
│   └── api_provider.py    # OpenAI-compatible API provider
├── retrieval/              # RAG System
│   ├── simple_rag.py      # Keyword + section-based retrieval
│   ├── database_rag.py    # Database-integrated RAG
│   └── rag_manager.py     # Unified RAG manager
├── tools/                  # MCP Tools
│   ├── mcp_toolkit.py     # Tool manager (DB health, log, monitor)
│   └── server.py          # MCP server
├── cases/                  # Case Management
│   ├── tracker.py         # Case lifecycle tracker
│   └── analyzer.py        # Analytics & visualization
├── sft/                    # SFT Fine-tuning
│   ├── data_collector.py  # Auto data collection
│   └── trainer.py         # Training config generator
├── web/                    # Web Applications
│   ├── streamlit_app.py   # 7-page Streamlit dashboard
│   └── fastapi_app.py     # FastAPI application
├── adapter/                # Platform Adapters
│   ├── feishu_adapter.py  # Feishu integration
│   └── privacy_adapter.py # Data privacy protection
├── assets/                 # Static assets
├── docs/                   # Documentation
├── data/                   # Data & Knowledge Base
├── demo/                   # React Interactive Demo
│   ├── src/               # React + TypeScript + shadcn/ui
│   └── dist/              # Built static files
├── Dockerfile
├── docker-compose.yml
└── LICENSE
```

---

## Configuration

### LLM Provider Options

| Provider | Config | Use Case |
|----------|--------|----------|
| OpenAI | `api_key` + `model: gpt-4o-mini` | Cloud API (recommended for quick start) |
| Azure OpenAI | `azure_endpoint` + `api_key` | Enterprise cloud |
| Ollama | `base_url: http://localhost:11434/v1` | Local deployment, privacy |
| vLLM | `base_url: http://localhost:8000/v1` | High-throughput local inference |

### Environment Variables

```bash
OPENAI_API_KEY=sk-...          # Required for OpenAI provider
LLM_PROVIDER=openai            # openai / azure / ollama / local
LLM_MODEL=gpt-4o-mini          # Default model
OPENAI_BASE_URL=...            # Custom endpoint URL
```

---

## Contact

- GitHub: [@rwlinno](https://github.com/rwlinno)

---

**DevOps-MAS** — Multi-Agent Intelligent DevOps System
