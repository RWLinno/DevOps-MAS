"""
DevOps-MAS - Modern Streamlit GUI
Full-featured dashboard with chat, case management, analytics, and SFT management.
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import streamlit as st
import pandas as pd

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.memory import AgentMemory
from cases.tracker import CaseTracker, CaseStatus, CasePriority, IncidentCase
from cases.analyzer import CaseAnalyzer
from sft.data_collector import SFTDataCollector
from sft.trainer import SFTTrainer
from llm.api_provider import APIModelProvider
from tools.mcp_toolkit import MCPToolkit
from retrieval.simple_rag import SimpleRAG

# ──────────────── Page Config ────────────────
st.set_page_config(
    page_title="DevOps-MAS",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────── CSS ────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.main-title { font-size: 2rem; font-weight: 700; color: #1a1a2e; margin-bottom: 0.2rem; }
.sub-title { font-size: 1rem; color: #6c757d; margin-bottom: 1.5rem; }
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.2rem; border-radius: 12px; color: white; text-align: center;
}
.metric-card h3 { font-size: 2rem; margin: 0; }
.metric-card p { font-size: 0.85rem; margin: 0; opacity: 0.9; }
.case-card {
    padding: 1rem; border-radius: 8px; margin-bottom: 0.8rem;
    border-left: 4px solid #667eea; background: #f8f9fa;
}
.case-card.p0 { border-left-color: #e74c3c; background: #fdf2f2; }
.case-card.p1 { border-left-color: #f39c12; background: #fefcf3; }
.case-card.p2 { border-left-color: #3498db; }
.case-card.p3 { border-left-color: #95a5a6; }
.chat-user {
    background: #e3f2fd; padding: 0.8rem 1rem; border-radius: 12px 12px 4px 12px;
    margin: 0.5rem 0; max-width: 80%; margin-left: auto; text-align: right;
}
.chat-assistant {
    background: #f5f5f5; padding: 0.8rem 1rem; border-radius: 12px 12px 12px 4px;
    margin: 0.5rem 0; max-width: 80%;
}
.chat-meta { font-size: 0.7rem; color: #999; margin-top: 0.3rem; }
.tag { display: inline-block; padding: 2px 8px; border-radius: 12px;
       background: #e8eaf6; color: #3f51b5; font-size: 0.75rem; margin: 2px; }
.status-badge { display: inline-block; padding: 3px 10px; border-radius: 12px;
                font-size: 0.75rem; font-weight: 600; }
.status-open { background: #fff3cd; color: #856404; }
.status-investigating { background: #cce5ff; color: #004085; }
.status-diagnosed { background: #d4edda; color: #155724; }
.status-resolved { background: #d1ecf1; color: #0c5460; }
.timeline-item { padding: 0.6rem 0; border-left: 2px solid #dee2e6; padding-left: 1rem; margin-left: 0.5rem; }
.timeline-dot { width: 10px; height: 10px; border-radius: 50%; background: #667eea;
                display: inline-block; margin-left: -1.35rem; margin-right: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# ──────────────── State Init ────────────────

@st.cache_resource
def get_memory():
    return AgentMemory(memory_dir=str(project_root / "data" / "memory"))

@st.cache_resource
def get_case_tracker():
    return CaseTracker(storage_dir=str(project_root / "data" / "test" / "cases"))

@st.cache_resource
def get_sft_collector():
    return SFTDataCollector(data_dir=str(project_root / "data" / "sft"))

@st.cache_resource
def get_llm_provider():
    config_path = project_root / "config.json"
    config = {}
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
    api_config = config.get("api_llm", {})
    return APIModelProvider(api_config)

@st.cache_resource
def get_mcp_toolkit():
    config_path = project_root / "config.json"
    config = {}
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
    return MCPToolkit(config.get("mcp", {}))

@st.cache_resource
def get_rag():
    docs_dir = project_root / "data" / "test" / "docs"
    if not docs_dir.exists():
        docs_dir = project_root / "data" / "documents"
    return SimpleRAG(documents_dir=str(docs_dir))

def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_case" not in st.session_state:
        st.session_state.current_case = None
    if "tool_results" not in st.session_state:
        st.session_state.tool_results = []

init_session()

# ──────────────── Sidebar ────────────────

def render_sidebar():
    with st.sidebar:
        st.markdown("## 🛡️ DevOps-MAS")
        st.caption("Intelligent Multi-Agent DevOps System")

        page = st.radio(
            "Navigation",
            ["💬 Chat", "📚 Knowledge Base", "🔌 Tools (MCP)", "📋 Cases", "📊 Analytics", "🔧 SFT Studio", "⚙️ Settings"],
            label_visibility="collapsed",
        )

        st.divider()
        memory = get_memory()
        stats = memory.get_stats()
        st.metric("Session Messages", stats["short_term_messages"])
        st.metric("Knowledge Base", stats["long_term_entries"])
        st.metric("Past Cases", stats["episodic_cases"])

        tracker = get_case_tracker()
        case_stats = tracker.get_stats()
        if case_stats.get("total", 0) > 0:
            st.divider()
            st.caption("Case Summary")
            cols = st.columns(2)
            cols[0].metric("Open", case_stats.get("by_status", {}).get("open", 0))
            cols[1].metric("Resolved", case_stats.get("by_status", {}).get("resolved", 0))

        return page


# ──────────────── Chat Page ────────────────

def render_chat():
    st.markdown('<div class="main-title">💬 Intelligent Q&A</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Ask any DevOps question — powered by multi-agent collaboration</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col2:
        uploaded_image = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg", "webp"], key="chat_image")
        active_case = st.selectbox(
            "Link to Case",
            ["None"] + [c.case_id for c in get_case_tracker().list_cases(limit=10)],
            key="link_case",
        )

    with col1:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                meta = msg.get("meta", "")
                st.markdown(
                    f'<div class="chat-assistant">{msg["content"]}'
                    f'<div class="chat-meta">{meta}</div></div>',
                    unsafe_allow_html=True,
                )

    query = st.chat_input("Describe your issue or ask a question...")
    if query:
        st.session_state.messages.append({"role": "user", "content": query})
        memory = get_memory()
        memory.add_message("user", query)

        with st.spinner("🤔 Multi-agent analysis in progress..."):
            response, meta = _process_query(query, uploaded_image, active_case)

        st.session_state.messages.append({"role": "assistant", "content": response, "meta": meta})
        memory.add_message("assistant", response)
        st.rerun()


def _process_query(query: str, image=None, case_id=None):
    """Process a query through the LLM with tool-use prompt."""
    llm = get_llm_provider()
    memory = get_memory()

    history = memory.get_context_window(max_tokens_estimate=3000)
    similar = memory.search_episodes(query, top_k=2)
    case_hint = ""
    if similar:
        for ep in similar:
            case_hint += f"\n[Past Case: {ep.title}] Root Cause: {ep.root_cause} | Solution: {ep.solution}\n"

    system_prompt = (
        "You are DevOps-MAS, an expert multi-agent DevOps assistant. "
        "You have access to specialized agents for: log analysis, metrics analysis, "
        "visual analysis, knowledge retrieval (RAG), web search, and comprehensive reasoning. "
        "Analyze the user's issue systematically: identify the problem, suggest diagnostics, "
        "and provide actionable solutions. Use structured markdown formatting."
    )
    if case_hint:
        system_prompt += f"\n\nRelevant past cases for reference:\n{case_hint}"

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history[-6:])
    messages.append({"role": "user", "content": query})

    image_path = None
    if image is not None:
        img_dir = project_root / "data" / "uploads"
        img_dir.mkdir(exist_ok=True)
        img_path = img_dir / image.name
        with open(img_path, "wb") as f:
            f.write(image.getbuffer())
        image_path = str(img_path)

    try:
        loop = asyncio.new_event_loop()
        resp = loop.run_until_complete(
            llm.generate(messages, image=image_path, max_tokens=2048, temperature=0.3)
        )
        loop.close()

        if resp.success:
            sft = get_sft_collector()
            sft.collect_from_interaction(query, resp.content, 0.85, "comprehensive_agent")

            meta_parts = [f"Model: {resp.model}"]
            if resp.latency_ms:
                meta_parts.append(f"Latency: {resp.latency_ms:.0f}ms")
            if resp.usage:
                meta_parts.append(f"Tokens: {resp.usage.get('total_tokens', '?')}")
            if case_id and case_id != "None":
                tracker = get_case_tracker()
                tracker.add_message(case_id, f"Q: {query}\nA: {resp.content[:200]}...", agent_name="chat")
                meta_parts.append(f"Linked: {case_id}")

            return resp.content, " | ".join(meta_parts)
        else:
            return f"⚠️ Error: {resp.error}\n\nPlease check your API key in Settings.", "Error"
    except Exception as e:
        return f"⚠️ Connection error: {e}\n\nMake sure LLM provider is configured in Settings.", "Error"


# ──────────────── Cases Page ────────────────

def render_cases():
    st.markdown('<div class="main-title">📋 Case Management</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Track incidents from creation to resolution</div>', unsafe_allow_html=True)

    tracker = get_case_tracker()

    tab1, tab2, tab3 = st.tabs(["📋 All Cases", "➕ New Case", "🔍 Case Detail"])

    with tab1:
        status_filter = st.selectbox("Filter by Status", ["All", "open", "investigating", "diagnosed", "resolved", "closed"])
        cases = tracker.list_cases(
            status=CaseStatus(status_filter) if status_filter != "All" else None,
            limit=50,
        )
        if not cases:
            st.info("No cases found.")
        for case in cases:
            priority_class = case.priority.value.lower()
            status_class = case.status.value
            res_time = f" | Resolved in {case.resolution_time_min:.0f}min" if case.resolution_time_min else ""
            tags_html = "".join(f'<span class="tag">{t}</span>' for t in case.tags)
            st.markdown(
                f'<div class="case-card {priority_class}">'
                f'<strong>{case.case_id}</strong> '
                f'<span class="status-badge status-{status_class}">{case.status.value.upper()}</span> '
                f'<span style="float:right;font-size:0.8rem;color:#666;">{case.priority.value}{res_time}</span>'
                f'<br/><strong>{case.title}</strong>'
                f'<br/><span style="font-size:0.85rem;color:#555;">{case.description[:150]}</span>'
                f'<br/>{tags_html}'
                f'</div>',
                unsafe_allow_html=True,
            )

    with tab2:
        with st.form("new_case"):
            title = st.text_input("Title")
            description = st.text_area("Description")
            priority = st.selectbox("Priority", ["P0", "P1", "P2", "P3"])
            tags_str = st.text_input("Tags (comma-separated)")
            submitted = st.form_submit_button("Create Case")
            if submitted and title:
                tags = [t.strip() for t in tags_str.split(",") if t.strip()]
                case = tracker.create_case(title, description, priority, tags)
                st.success(f"Case {case.case_id} created!")
                st.rerun()

    with tab3:
        case_ids = [c.case_id for c in tracker.list_cases(limit=50)]
        if case_ids:
            selected = st.selectbox("Select Case", case_ids)
            case = tracker.get_case(selected)
            if case:
                _render_case_detail(case, tracker)
        else:
            st.info("No cases available.")


def _render_case_detail(case: IncidentCase, tracker: CaseTracker):
    col1, col2, col3 = st.columns(3)
    col1.metric("Priority", case.priority.value)
    col2.metric("Status", case.status.value.upper())
    col3.metric("Resolution Time", f"{case.resolution_time_min:.0f}min" if case.resolution_time_min else "Pending")

    st.subheader(case.title)
    st.write(case.description)

    if case.root_cause:
        st.markdown(f"**Root Cause:** {case.root_cause}")
    if case.solution:
        st.markdown(f"**Solution:** {case.solution}")

    st.subheader("📜 Timeline")
    for event in case.events:
        ts = datetime.fromtimestamp(event.timestamp).strftime("%H:%M:%S")
        agent = f" [{event.agent_name}]" if event.agent_name else ""
        icon = {"created": "🟢", "diagnosis": "🔍", "resolution": "✅", "message": "💬", "status_change": "🔄"}.get(event.event_type, "📌")
        st.markdown(
            f'<div class="timeline-item"><span class="timeline-dot"></span>'
            f'<strong>{ts}</strong> {icon}{agent} — {event.content}</div>',
            unsafe_allow_html=True,
        )

    st.subheader("⚡ Actions")
    col1, col2 = st.columns(2)
    with col1:
        new_status = st.selectbox("Change Status", [s.value for s in CaseStatus], key=f"status_{case.case_id}")
        if st.button("Update Status", key=f"btn_status_{case.case_id}"):
            tracker.update_status(case.case_id, CaseStatus(new_status))
            st.success("Status updated!")
            st.rerun()
    with col2:
        note = st.text_area("Add Note", key=f"note_{case.case_id}")
        if st.button("Add Note", key=f"btn_note_{case.case_id}"):
            tracker.add_message(case.case_id, note)
            st.success("Note added!")
            st.rerun()


# ──────────────── Analytics Page ────────────────

def render_analytics():
    st.markdown('<div class="main-title">📊 Analytics Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Insights from DevOps operations</div>', unsafe_allow_html=True)

    tracker = get_case_tracker()
    analyzer = CaseAnalyzer(tracker)
    report = analyzer.generate_report()
    viz_data = analyzer.get_visualization_data()

    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f'<div class="metric-card"><h3>{report.total_cases}</h3><p>Total Cases</p></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="metric-card"><h3>{report.resolved_cases}</h3><p>Resolved</p></div>', unsafe_allow_html=True)
    avg_time = f"{report.avg_resolution_time_min:.0f}min" if report.avg_resolution_time_min else "N/A"
    col3.markdown(f'<div class="metric-card"><h3>{avg_time}</h3><p>Avg Resolution</p></div>', unsafe_allow_html=True)
    open_count = report.status_distribution.get("open", 0)
    col4.markdown(f'<div class="metric-card"><h3>{open_count}</h3><p>Open Cases</p></div>', unsafe_allow_html=True)

    st.divider()

    if viz_data.get("empty"):
        st.info("No data available for visualization.")
        return

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Priority Distribution")
        if viz_data.get("priority_distribution"):
            df = pd.DataFrame(
                list(viz_data["priority_distribution"].items()),
                columns=["Priority", "Count"],
            )
            st.bar_chart(df.set_index("Priority"))

    with col2:
        st.subheader("Status Distribution")
        if viz_data.get("status_distribution"):
            df = pd.DataFrame(
                list(viz_data["status_distribution"].items()),
                columns=["Status", "Count"],
            )
            st.bar_chart(df.set_index("Status"))

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top Issue Tags")
        if viz_data.get("top_tags"):
            df = pd.DataFrame(
                list(viz_data["top_tags"].items()),
                columns=["Tag", "Count"],
            ).sort_values("Count", ascending=True)
            st.bar_chart(df.set_index("Tag"))

    with col2:
        st.subheader("Avg Resolution by Priority")
        if viz_data.get("avg_resolution_by_priority"):
            df = pd.DataFrame(
                list(viz_data["avg_resolution_by_priority"].items()),
                columns=["Priority", "Avg Minutes"],
            )
            st.bar_chart(df.set_index("Priority"))

    st.divider()
    st.subheader("💡 Recommendations")
    for rec in report.recommendations:
        st.markdown(f"- {rec}")

    sft = get_sft_collector()
    sft_stats = sft.get_stats()
    st.divider()
    st.subheader("🧠 SFT Dataset Stats")
    cols = st.columns(3)
    cols[0].metric("Total Samples", sft_stats["total_samples"])
    cols[1].metric("Avg Quality", f"{sft_stats['avg_quality_score']:.2f}")
    cols[2].metric("High Quality (>0.8)", sft_stats["high_quality_count"])


# ──────────────── SFT Studio ────────────────

def render_sft_studio():
    st.markdown('<div class="main-title">🔧 SFT Studio</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Manage fine-tuning data and launch training</div>', unsafe_allow_html=True)

    collector = get_sft_collector()
    trainer = SFTTrainer(data_dir=str(project_root / "data" / "sft"))

    tab1, tab2, tab3 = st.tabs(["📝 Dataset", "➕ Add Sample", "🚀 Training"])

    with tab1:
        stats = collector.get_stats()
        cols = st.columns(4)
        cols[0].metric("Total Samples", stats["total_samples"])
        cols[1].metric("Avg Quality", f"{stats['avg_quality_score']:.2f}")
        cols[2].metric("High Quality", stats["high_quality_count"])
        cols[3].metric("Categories", len(stats.get("by_category", {})))

        if stats.get("by_category"):
            st.subheader("By Category")
            df = pd.DataFrame(
                list(stats["by_category"].items()),
                columns=["Category", "Count"],
            )
            st.bar_chart(df.set_index("Category"))

        st.subheader("Export Dataset")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Export Alpaca Format"):
                path = collector.export_to_file("alpaca")
                st.success(f"Exported to {path}")
        with col2:
            if st.button("Export ShareGPT Format"):
                path = collector.export_to_file("sharegpt")
                st.success(f"Exported to {path}")

    with tab2:
        with st.form("add_sft"):
            instruction = st.text_area("Instruction (Question)")
            context = st.text_area("Context (Optional)")
            output = st.text_area("Expected Output (Answer)")
            category = st.selectbox("Category", ["log_analysis", "metrics", "visual", "knowledge", "retrieval", "case_resolution", "general"])
            submitted = st.form_submit_button("Add Sample")
            if submitted and instruction and output:
                collector.add_manual_sample(instruction, output, context, category)
                st.success("Sample added!")
                st.rerun()

    with tab3:
        st.subheader("Training Configuration")
        configs = trainer.get_recommended_configs()
        selected_config = st.selectbox("Preset", list(configs.keys()))
        cfg = configs[selected_config]
        st.json(cfg)

        if st.button("Generate Training Config & Script"):
            config = trainer.generate_training_config(
                base_model=cfg["base_model"],
                method=cfg.get("method", "lora"),
                num_epochs=cfg["epochs"],
                batch_size=cfg["batch_size"],
                lora_rank=cfg.get("lora_rank", 16),
            )
            script_path = trainer.generate_launch_script()
            st.success(f"Config and script generated!")
            st.code(f"bash {script_path}", language="bash")


# ──────────────── Knowledge Base ────────────────

def render_knowledge_base():
    st.markdown('<div class="main-title">📚 Knowledge Base (RAG)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Document retrieval and knowledge management powered by SimpleRAG</div>', unsafe_allow_html=True)

    rag = get_rag()

    tab1, tab2, tab3 = st.tabs(["🔍 Search", "📄 Documents", "📊 RAG Stats"])

    with tab1:
        query = st.text_input("Search knowledge base", placeholder="e.g. Redis连接超时怎么排查？")
        top_k = st.slider("Results count", 1, 10, 3)
        if query:
            results = rag.search_documents(query, top_k=top_k)
            if results:
                for i, r in enumerate(results, 1):
                    with st.expander(f"#{i} {r.document.title} (score: {r.score:.3f})", expanded=(i == 1)):
                        st.markdown(f"**Category:** `{r.document.category}` | **File:** `{r.document.file_path}`")
                        if r.matched_sections:
                            st.markdown("**Matched sections:**")
                            for section in r.matched_sections[:3]:
                                st.info(section[:500])
                        st.markdown("**Context:**")
                        st.text(r.context[:800])
            else:
                st.warning("No results found. Try different keywords.")

        st.divider()
        st.subheader("Example Queries")
        example_cols = st.columns(3)
        examples = [
            "Redis连接超时排查步骤",
            "MySQL慢查询优化",
            "Kafka consumer lag处理",
        ]
        for col, ex in zip(example_cols, examples):
            if col.button(ex, key=f"rag_ex_{ex}"):
                st.session_state["rag_query"] = ex
                st.rerun()

    with tab2:
        docs = list(rag.documents.values())
        if docs:
            st.metric("Total Documents", len(docs))
            for doc in docs:
                with st.expander(f"📄 {doc.title} [{doc.category}]"):
                    st.markdown(f"**ID:** `{doc.id}` | **Path:** `{doc.file_path}`")
                    st.text_area("Content preview", doc.content[:2000], height=200, key=f"doc_{doc.id}", disabled=True)
        else:
            st.info("No documents loaded. Add .md files to the documents directory.")

    with tab3:
        docs = list(rag.documents.values())
        col1, col2, col3 = st.columns(3)
        col1.markdown(f'<div class="metric-card"><h3>{len(docs)}</h3><p>Documents</p></div>', unsafe_allow_html=True)
        categories = set(d.category for d in docs) if docs else set()
        col2.markdown(f'<div class="metric-card"><h3>{len(categories)}</h3><p>Categories</p></div>', unsafe_allow_html=True)
        total_chars = sum(len(d.content) for d in docs) if docs else 0
        col3.markdown(f'<div class="metric-card"><h3>{total_chars:,}</h3><p>Total Characters</p></div>', unsafe_allow_html=True)

        if docs:
            cat_counts = {}
            for d in docs:
                cat_counts[d.category] = cat_counts.get(d.category, 0) + 1
            df = pd.DataFrame(list(cat_counts.items()), columns=["Category", "Count"])
            st.bar_chart(df.set_index("Category"))

        st.divider()
        memory = get_memory()
        episodes = memory.get_all_episodes()
        st.subheader("🧠 Episodic Memory (Resolved Cases)")
        if episodes:
            for ep in episodes:
                with st.expander(f"📋 {ep.title} [{ep.case_id}]"):
                    st.markdown(f"**Root Cause:** {ep.root_cause}")
                    st.markdown(f"**Solution:** {ep.solution}")
                    st.markdown(f"**Tags:** {', '.join(ep.tags)}")
                    st.markdown(f"**Resolution Time:** {ep.resolution_time_min:.0f} min")
                    if ep.steps:
                        st.markdown("**Steps:**")
                        for j, step in enumerate(ep.steps, 1):
                            st.markdown(f"  {j}. {step}")
        else:
            st.info("No episodic memories yet. They are created when cases are resolved.")


# ──────────────── Tools (MCP) ────────────────

def render_tools():
    st.markdown('<div class="main-title">🔌 Tools (MCP)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Model Context Protocol — external tool integration for diagnostics</div>', unsafe_allow_html=True)

    toolkit = get_mcp_toolkit()
    tools = toolkit.get_available_tools()

    tab1, tab2 = st.tabs(["🛠️ Available Tools", "▶️ Execute Tool"])

    with tab1:
        if not tools:
            st.warning("No MCP tools available.")
        for tool in tools:
            with st.expander(f"🔧 {tool['name']} — {tool['description']}", expanded=True):
                params = tool.get("parameters", {}).get("properties", {})
                required = tool.get("parameters", {}).get("required", [])
                if params:
                    cols = st.columns([1, 1, 1, 2])
                    cols[0].markdown("**Parameter**")
                    cols[1].markdown("**Type**")
                    cols[2].markdown("**Required**")
                    cols[3].markdown("**Description**")
                    for pname, pinfo in params.items():
                        cols = st.columns([1, 1, 1, 2])
                        cols[0].code(pname)
                        cols[1].write(pinfo.get("type", "string"))
                        cols[2].write("Yes" if pname in required else "No")
                        desc = pinfo.get("description", "")
                        if "enum" in pinfo:
                            desc += f" (options: {', '.join(pinfo['enum'])})"
                        cols[3].write(desc)

    with tab2:
        tool_names = [t["name"] for t in tools]
        if not tool_names:
            st.info("No tools available to execute.")
            return

        selected_tool = st.selectbox("Select Tool", tool_names)
        selected_schema = next((t for t in tools if t["name"] == selected_tool), None)

        st.markdown(f"**Description:** {selected_schema['description']}")

        params_input = {}
        if selected_schema:
            props = selected_schema.get("parameters", {}).get("properties", {})
            for pname, pinfo in props.items():
                ptype = pinfo.get("type", "string")
                desc = pinfo.get("description", pname)
                if "enum" in pinfo:
                    params_input[pname] = st.selectbox(desc, pinfo["enum"], key=f"tool_{pname}")
                elif ptype == "integer":
                    params_input[pname] = st.number_input(desc, value=pinfo.get("default", 50), step=1, key=f"tool_{pname}")
                else:
                    params_input[pname] = st.text_input(desc, value=pinfo.get("default", ""), key=f"tool_{pname}")

        if st.button("Execute Tool", type="primary"):
            clean_params = {k: v for k, v in params_input.items() if v}
            with st.spinner(f"Executing {selected_tool}..."):
                try:
                    loop = asyncio.new_event_loop()
                    result = loop.run_until_complete(toolkit.execute_tool(selected_tool, clean_params))
                    loop.close()
                    st.success("Execution complete!")
                    st.json(result)
                    st.session_state.tool_results.append({
                        "tool": selected_tool,
                        "params": clean_params,
                        "result": result,
                        "time": datetime.now().strftime("%H:%M:%S"),
                    })
                except Exception as e:
                    st.error(f"Execution failed: {e}")

        if st.session_state.tool_results:
            st.divider()
            st.subheader("📜 Execution History")
            for i, tr in enumerate(reversed(st.session_state.tool_results[-10:])):
                with st.expander(f"[{tr['time']}] {tr['tool']}({tr['params']})", expanded=(i == 0)):
                    st.json(tr["result"])


# ──────────────── Settings ────────────────

def render_settings():
    st.markdown('<div class="main-title">⚙️ Settings</div>', unsafe_allow_html=True)

    config_path = project_root / "config.json"
    config = {}
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)

    st.subheader("LLM Provider")
    provider = st.selectbox("Provider", ["openai", "azure", "ollama", "local"], index=0)
    api_key = st.text_input("API Key", value=config.get("api_llm", {}).get("api_key", ""), type="password")
    base_url = st.text_input("Base URL", value=config.get("api_llm", {}).get("base_url", "https://api.openai.com/v1"))
    model = st.text_input("Default Model", value=config.get("api_llm", {}).get("model", "gpt-4o-mini"))

    if st.button("Save Settings"):
        config["api_llm"] = {
            "provider": provider,
            "api_key": api_key,
            "base_url": base_url,
            "model": model,
        }
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        st.success("Settings saved! Restart the app to apply.")
        st.cache_resource.clear()

    st.divider()
    st.subheader("System Info")
    memory = get_memory()
    st.json(memory.get_stats())

    st.subheader("Environment Variables")
    st.code(
        f"OPENAI_API_KEY={'Set' if os.getenv('OPENAI_API_KEY') else 'Not set'}\n"
        f"LLM_PROVIDER={os.getenv('LLM_PROVIDER', 'Not set')}\n"
        f"LLM_MODEL={os.getenv('LLM_MODEL', 'Not set')}",
        language="bash",
    )


# ──────────────── Main ────────────────

def main():
    page = render_sidebar()
    if page == "💬 Chat":
        render_chat()
    elif page == "📚 Knowledge Base":
        render_knowledge_base()
    elif page == "🔌 Tools (MCP)":
        render_tools()
    elif page == "📋 Cases":
        render_cases()
    elif page == "📊 Analytics":
        render_analytics()
    elif page == "🔧 SFT Studio":
        render_sft_studio()
    elif page == "⚙️ Settings":
        render_settings()


if __name__ == "__main__":
    main()
