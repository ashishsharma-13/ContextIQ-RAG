import os
import sys
import base64
import uuid
from pathlib import Path
from datetime import datetime
import streamlit as st
import requests

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import settings

LOGO_PATH = ROOT_DIR / "app" / "frontend" / "assets" / "logo.jpg"


def get_base64_image(image_path: Path) -> str:
    """Helper to convert image file to base64 data URI for inline HTML rendering."""
    if image_path.exists():
        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            return f"data:image/jpeg;base64,{encoded}"
    return ""


LOGO_DATA_URL = get_base64_image(LOGO_PATH)

# Page Configuration
st.set_page_config(
    page_title="ContextIQ - Personal Knowledge Assistant",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Sleek Dark Theme CSS matching exact reference UI
st.markdown("""
    <style>
    /* Global Page Styling */
    .stApp {
        background-color: #0B0F19;
        color: #F1F5F9;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    /* Reduce Streamlit Default Top Padding & Header Bar Height */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        height: 2rem !important;
    }
    .main .block-container {
        max-width: 1080px !important;
        padding-top: 1rem !important;
        padding-bottom: 3rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        margin: 0 auto !important;
    }
    [data-testid="stSidebarUserContent"] {
        padding-top: 1.2rem !important;
    }
    
    /* Sidebar Styling & Width Alignment */
    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1F2937;
        min-width: 320px !important;
        max-width: 340px !important;
    }
    .sidebar-brand-title {
        font-size: 1.75rem;
        font-weight: 800;
        color: #60A5FA;
        margin-bottom: 0px;
        line-height: 1.15;
        letter-spacing: -0.01em;
    }
    .sidebar-brand-sub {
        font-size: 0.88rem;
        color: #9CA3AF;
        margin-bottom: 18px;
    }
    
    /* Model & Status Badges */
    .sidebar-section-title {
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #6B7280;
        margin-top: 16px;
        margin-bottom: 8px;
    }
    .model-info-card {
        background-color: #1F2937;
        border: 1px solid #374151;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 14px;
    }
    .model-name-title {
        font-weight: 700;
        font-size: 0.92rem;
        color: #38BDF8;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .model-detail-sub {
        font-size: 0.78rem;
        color: #9CA3AF;
        margin-top: 4px;
    }
    .status-pill-green {
        background-color: #064E3B;
        color: #34D399;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .privacy-pill {
        background-color: #1E1B4B;
        color: #A5B4FC;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 5px;
        border: 1px solid #312E81;
    }
    
    /* Knowledge Base Metric Boxes */
    .metric-card-box {
        background-color: #1F2937;
        border: 1px solid #374151;
        border-radius: 10px;
        padding: 14px;
        text-align: center;
    }
    .metric-card-num {
        font-size: 1.5rem;
        font-weight: 800;
        color: #F9FAFB;
    }
    .metric-card-label {
        font-size: 0.78rem;
        color: #9CA3AF;
        margin-top: 2px;
    }

    /* Main Header Area */
    .header-container {
        display: flex;
        align-items: flex-start;
        gap: 18px;
        margin-bottom: 24px;
    }
    .header-icon-box {
        background-color: #1D4ED8;
        border-radius: 14px;
        padding: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #F9FAFB;
        line-height: 1.1;
        margin-bottom: 4px;
    }
    .main-subtitle {
        font-size: 1.05rem;
        font-weight: 600;
        color: #93C5FD;
        margin-bottom: 4px;
    }
    .main-desc {
        font-size: 0.92rem;
        color: #9CA3AF;
    }

    /* Source Reference Cards */
    .source-card {
        background-color: #1F2937;
        border-left: 4px solid #3B82F6;
        border-top: 1px solid #374151;
        border-right: 1px solid #374151;
        border-bottom: 1px solid #374151;
        padding: 12px 16px;
        margin-top: 8px;
        margin-bottom: 8px;
        border-radius: 8px;
    }
    .source-title {
        font-weight: 700;
        color: #60A5FA;
        font-size: 0.9rem;
    }
    .category-badge {
        background-color: #1E3A8A;
        color: #93C5FD;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .source-snippet {
        font-size: 0.85rem;
        color: #D1D5DB;
        font-style: italic;
        margin-top: 6px;
    }

    /* Unified Single-Row Search & Controls Dock Bar */
    .st-key-chat_unified_bar {
        position: fixed !important;
        bottom: 24px !important;
        left: calc(50% + 160px) !important;
        transform: translateX(-50%) !important;
        width: min(920px, 82%) !important;
        z-index: 999 !important;
        background-color: rgba(17, 24, 39, 0.96) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid #374151 !important;
        border-radius: 18px !important;
        padding: 6px 12px !important;
        box-shadow: 0 12px 30px -5px rgba(0, 0, 0, 0.6) !important;
    }

    /* Keep unified dock bar aligned when sidebar collapses */
    [data-testid="stSidebar"][aria-expanded="false"] ~ .main .st-key-chat_unified_bar {
        left: 50% !important;
    }

    @media (max-width: 768px) {
        .st-key-chat_unified_bar {
            left: 50% !important;
            width: 95% !important;
            padding: 4px 8px !important;
        }
    }

    /* Style the inline chat_input inside the unified dock bar */
    .st-key-chat_unified_bar [data-testid="stChatInput"] {
        position: static !important;
        transform: none !important;
        width: 100% !important;
        background-color: #0F172A !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        box-shadow: none !important;
        margin: 0 !important;
    }

    /* Style selectboxes inside unified dock bar */
    .st-key-chat_unified_bar [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background-color: #0F172A !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        font-size: 0.84rem !important;
        font-weight: 500 !important;
        color: #F1F5F9 !important;
        height: 42px !important;
    }

    /* Style clear chat button inside unified dock bar */
    .st-key-chat_unified_bar button {
        border-radius: 12px !important;
        border: 1px solid #374151 !important;
        background-color: #1F2937 !important;
        color: #9CA3AF !important;
        height: 42px !important;
    }
    .st-key-chat_unified_bar button:hover {
        background-color: #374151 !important;
        color: #EF4444 !important;
        border-color: #EF4444 !important;
    }

    .chat-bottom-spacer {
        height: 110px !important;
    }
    .chat-footer-hint {
        position: fixed;
        bottom: 6px;
        left: calc(50% + 160px);
        transform: translateX(-50%);
        z-index: 1000;
        font-size: 0.74rem;
        color: #6B7280;
        text-align: center;
        width: 100%;
        pointer-events: none;
    }
    [data-testid="stSidebar"][aria-expanded="false"] ~ .main .chat-footer-hint {
        left: 50% !important;
    }

    /* Executive Tab Navigation Styling */
    div[data-baseweb="tab-list"] {
        gap: 8px !important;
        border-bottom: 1px solid #1F2937 !important;
        background-color: transparent !important;
    }
    button[data-baseweb="tab"] {
        color: #9CA3AF !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        padding: 8px 18px !important;
        background-color: transparent !important;
        border: none !important;
    }
    button[data-baseweb="tab"]:hover {
        color: #F1F5F9 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #60A5FA !important;
    }
    div[data-baseweb="tab-highlight"] {
        background-color: #3B82F6 !important;
        height: 2px !important;
    }

    /* Professional Document Table Styling */
    .table-header-col {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #9CA3AF;
        padding-bottom: 6px;
    }
    .table-cell-text {
        font-size: 0.84rem;
        color: #E2E8F0;
        line-height: 1.4;
    }
    .category-pill {
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 600;
        display: inline-block;
        letter-spacing: 0.02em;
    }
    .cat-academic { background-color: #1E3A8A; color: #93C5FD; border: 1px solid #1D4ED8; }
    .cat-it { background-color: #083344; color: #67E8F9; border: 1px solid #0E7490; }
    .cat-projects { background-color: #3B0764; color: #D8B4FE; border: 1px solid #7E22CE; }
    .cat-policies { background-color: #451A03; color: #FCD34D; border: 1px solid #B45309; }
    .cat-notices { background-color: #431407; color: #FDBA74; border: 1px solid #C2410C; }
    .cat-guides { background-color: #064E3B; color: #6EE7B7; border: 1px solid #047857; }
    .cat-faqs { background-color: #172554; color: #93C5FD; border: 1px solid #2563EB; }
    .cat-research { background-color: #042F2E; color: #5EEAD4; border: 1px solid #0D9488; }
    .cat-other { background-color: #1E293B; color: #94A3B8; border: 1px solid #334155; }

    /* Delete Button Polish */
    .doc-row-del button {
        background-color: transparent !important;
        border: 1px solid #374151 !important;
        color: #9CA3AF !important;
        border-radius: 6px !important;
        padding: 2px 6px !important;
        transition: all 0.2s ease !important;
    }
    .doc-row-del button:hover {
        background-color: #7F1D1D !important;
        border-color: #EF4444 !important;
        color: #FEE2E2 !important;
    }
    </style>
""", unsafe_allow_html=True)


BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")


# Initialize Session State
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

if "messages" not in st.session_state:
    st.session_state.messages = []

if "user_api_key" not in st.session_state:
    st.session_state.user_api_key = ""

if "provider_choice" not in st.session_state:
    st.session_state.provider_choice = "Auto-detect"


def check_backend_health(session_id: str):
    """Checks if FastAPI backend is online."""
    try:
        res = requests.get(f"{BACKEND_URL}/health", headers={"x-session-id": session_id}, timeout=2)
        if res.status_code == 200:
            return True, res.json().get("vector_store", {})
    except Exception:
        pass
    return False, {}


# Direct Python Fallback functions with Session Privacy
def direct_upload(files, category, session_id: str):
    from app.rag.loader import load_pdf_document
    from app.rag.splitter import split_documents
    from app.rag.vectorstore import add_chunks_to_vectorstore, is_document_already_indexed

    session_dir = Path(settings.DOCUMENTS_DIR) / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    processed = []
    seen = set()
    for file in files:
        if file.name.lower() in seen or is_document_already_indexed(file.name, session_id=session_id):
            raise ValueError(f"Document '{file.name}' is already uploaded in your workspace. Please delete it before re-uploading.")
        seen.add(file.name.lower())

        doc_id = str(uuid.uuid4())
        safe_filename = f"{doc_id}_{file.name}"
        save_path = session_dir / safe_filename
        with open(save_path, "wb") as f:
            f.write(file.getvalue())

        docs = load_pdf_document(str(save_path), document_id=doc_id, category=category)
        for d in docs:
            d.metadata["source"] = file.name
            d.metadata["session_id"] = session_id

        chunks = split_documents(docs)
        add_chunks_to_vectorstore(chunks, session_id=session_id)
        processed.append(file.name)
    return processed


def direct_ask(question, category, top_k, api_key, provider, session_id: str):
    from app.rag.chain import ask_question
    cat_filter = None if category == "All" else category
    return ask_question(
        question=question,
        category_filter=cat_filter,
        top_k=top_k,
        api_key=api_key,
        provider=provider,
        session_id=session_id
    )


def direct_list_docs(session_id: str):
    from app.rag.vectorstore import get_indexed_documents
    return get_indexed_documents(session_id=session_id)


def direct_delete_doc(doc_id: str, session_id: str):
    from app.rag.vectorstore import delete_document_by_id, get_indexed_documents
    docs = get_indexed_documents(session_id=session_id)
    target = next((d for d in docs if d["document_id"] == doc_id), None)
    deleted_chunks = delete_document_by_id(doc_id, session_id=session_id)
    if target and target.get("file_path"):
        p = Path(target["file_path"])
        if p.exists():
            os.remove(p)
    return deleted_chunks


# Active Provider & Key Resolution
env_groq_key = settings.get_groq_api_key()
env_openai_key = settings.get_openai_api_key()
typed_key = st.session_state.user_api_key.strip()

# Resolve provider
choice = st.session_state.provider_choice
if choice == "OpenAI":
    active_provider = "openai"
    active_key = typed_key or env_openai_key
elif choice == "Groq":
    active_provider = "groq"
    active_key = typed_key or env_groq_key
else:  # Auto-detect
    if typed_key:
        active_provider = settings.detect_provider(key=typed_key)
        active_key = typed_key
    elif env_groq_key:
        active_provider = "groq"
        active_key = env_groq_key
    elif env_openai_key:
        active_provider = "openai"
        active_key = env_openai_key
    else:
        active_provider = settings.LLM_PROVIDER
        active_key = ""

active_model_name = settings.OPENAI_MODEL if active_provider == "openai" else settings.GROQ_MODEL


# ================= SIDEBAR UI =================
with st.sidebar:
    # Sidebar Header Brand with Logo
    if LOGO_DATA_URL:
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 16px;">
            <img src="{LOGO_DATA_URL}" style="width: 58px; height: 58px; border-radius: 14px; object-fit: cover; border: 1px solid #374151; box-shadow: 0 4px 14px rgba(0,0,0,0.35);">
            <div>
                <div class="sidebar-brand-title" style="font-size: 1.75rem; line-height: 1.15;">ContextIQ</div>
                <div class="sidebar-brand-sub" style="margin-bottom: 0; font-size: 0.88rem;">Knowledge Assistant</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="sidebar-brand-title">ContextIQ</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-brand-sub">Your Personal Knowledge Assistant</div>', unsafe_allow_html=True)

    st.divider()

    # Active Model Card
    st.markdown('<div class="sidebar-section-title">Model Architecture</div>', unsafe_allow_html=True)
    engine_label = "OpenAI" if active_provider == "openai" else "Groq"
    st.markdown(f"""
    <div class="model-info-card">
        <div class="model-name-title">
            <span><svg style="width:14px;height:14px;fill:#F59E0B;vertical-align:-2px;margin-right:4px;" viewBox="0 0 24 24"><path d="M7 2v11h3v9l7-12h-4l4-8z"/></svg> Engine:</span> {engine_label}
        </div>
        <div class="model-detail-sub"><b>LLM:</b> {active_model_name}</div>
        <div class="model-detail-sub"><b>Embeddings:</b> HuggingFace (all-MiniLM-L6-v2)</div>
    </div>
    """, unsafe_allow_html=True)

    # API Key & Provider Configuration
    st.markdown('<div class="sidebar-section-title">API Key & Provider</div>', unsafe_allow_html=True)

    provider_options = ["Auto-detect", "Groq", "OpenAI"]
    selected_p = st.selectbox(
        "Provider",
        provider_options,
        index=provider_options.index(st.session_state.provider_choice) if st.session_state.provider_choice in provider_options else 0,
        key="provider_select_widget"
    )
    if selected_p != st.session_state.provider_choice:
        st.session_state.provider_choice = selected_p
        st.rerun()

    # Show status badge if key is active; only show warning if NO key exists
    if active_key:
        key_source = "Session input" if typed_key else "Environment / Secrets"
        st.markdown(f"""
        <div style="margin-bottom: 8px;">
            <span class="status-pill-green">● Connected: {active_provider.capitalize()}</span>
            <div style="font-size: 0.75rem; color: #9CA3AF; margin-top: 4px;">Source: {key_source}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("No API Key configured. Please enter your Groq or OpenAI key below.", icon=":material/vpn_key:")

    input_key = st.text_input(
        "Enter API Key",
        value=st.session_state.user_api_key,
        type="password",
        placeholder="gsk_... or sk-...",
        help="Paste your Groq or OpenAI API key here. It remains secure in your browser session."
    )
    if input_key != st.session_state.user_api_key:
        st.session_state.user_api_key = input_key.strip()
        st.rerun()

    st.divider()

    # Workspace Privacy Section
    st.markdown('<div class="sidebar-section-title">Private Workspace</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
        <span style="font-size: 0.85rem; color: #D1D5DB;">Workspace ID</span>
        <span class="privacy-pill">🔒 {st.session_state.session_id}</span>
    </div>
    <div style="font-size: 0.74rem; color: #9CA3AF; margin-bottom: 8px;">
        Documents you upload are private to your workspace and cannot be seen by others.
    </div>
    """, unsafe_allow_html=True)

    with st.expander("Switch or Restore Workspace", expanded=False):
        new_sid = st.text_input("Workspace Key", value=st.session_state.session_id, key="sid_input")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if st.button("Apply", key="apply_sid"):
                if new_sid.strip() and new_sid.strip() != st.session_state.session_id:
                    st.session_state.session_id = new_sid.strip()
                    st.rerun()
        with col_s2:
            if st.button("New Private", key="new_sid"):
                st.session_state.session_id = str(uuid.uuid4())[:8]
                st.session_state.messages = []
                st.rerun()

    st.divider()

    # System Status
    st.markdown('<div class="sidebar-section-title">System Status</div>', unsafe_allow_html=True)
    backend_online, vector_stats = check_backend_health(st.session_state.session_id)
    if backend_online:
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
            <span style="font-size: 0.88rem; color: #D1D5DB;">FastAPI Backend</span>
            <span class="status-pill-green">● Connected</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
            <span style="font-size: 0.88rem; color: #D1D5DB;">Engine</span>
            <span style="background-color: #1E3A8A; color: #93C5FD; padding: 4px 12px; border-radius: 12px; font-size: 0.8rem; font-weight: 600;">Direct Python</span>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Knowledge Base Metric Cards (Scoped to Current Session)
    st.markdown('<div class="sidebar-section-title">Your Knowledge Base</div>', unsafe_allow_html=True)
    if backend_online and vector_stats:
        total_docs = vector_stats.get("total_documents", 0)
        total_chunks = vector_stats.get("total_chunks", 0)
    else:
        from app.rag.vectorstore import get_vectorstore_stats
        try:
            stats = get_vectorstore_stats(session_id=st.session_state.session_id)
            total_docs = stats.get("total_documents", 0)
            total_chunks = stats.get("total_chunks", 0)
        except Exception:
            total_docs, total_chunks = 0, 0

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown(f"""
        <div class="metric-card-box">
            <div style="color: #60A5FA; display: flex; justify-content: center; margin-bottom: 4px;">
                <svg style="width:22px;height:22px;fill:currentColor;" viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/></svg>
            </div>
            <div class="metric-card-num">{total_docs}</div>
            <div class="metric-card-label">Your Docs</div>
        </div>
        """, unsafe_allow_html=True)
    with col_m2:
        st.markdown(f"""
        <div class="metric-card-box">
            <div style="color: #60A5FA; display: flex; justify-content: center; margin-bottom: 4px;">
                <svg style="width:22px;height:22px;fill:currentColor;" viewBox="0 0 24 24"><path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H8V4h12v12z"/></svg>
            </div>
            <div class="metric-card-num">{total_chunks}</div>
            <div class="metric-card-label">Your Chunks</div>
        </div>
        """, unsafe_allow_html=True)




# ================= MAIN AREA UI =================

# Header Block with Project Logo
if LOGO_DATA_URL:
    st.markdown(f"""
    <div class="header-container">
        <div style="background-color: #1F2937; border: 1px solid #374151; border-radius: 16px; padding: 6px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
            <img src="{LOGO_DATA_URL}" style="width: 64px; height: 64px; border-radius: 12px; object-fit: cover;">
        </div>
        <div>
            <div class="main-title">ContextIQ</div>
            <div class="main-subtitle">Context-Aware Personal Knowledge Assistant</div>
            <div class="main-desc">Upload your documents and ask natural language questions with exact page citations.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="header-container">
        <div class="header-icon-box">
            <svg style="width:32px;height:32px;fill:#FFFFFF;" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>
        </div>
        <div>
            <div class="main-title">ContextIQ</div>
            <div class="main-subtitle">Context-Aware Personal Knowledge Assistant</div>
            <div class="main-desc">Upload your documents and ask natural language questions with exact page citations.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Navigation Tabs
tab_chat, tab_docs, tab_guide = st.tabs(["Ask Assistant", "Document Management", "How to Use?"])


# ================= TAB 1: ASK ASSISTANT =================
assistant_avatar = str(LOGO_PATH) if LOGO_PATH.exists() else ":material/smart_toy:"

with tab_chat:
    # 1. Render all chat messages chronologically from TOP to BOTTOM
    if not st.session_state.messages:
        with st.chat_message("assistant", avatar=assistant_avatar):
            st.markdown("Hello! I am **ContextIQ**, your personal context-aware knowledge assistant. Ask me a question about your uploaded documents.")

    for msg in st.session_state.messages:
        avatar_icon = ":material/person:" if msg["role"] == "user" else assistant_avatar
        with st.chat_message(msg["role"], avatar=avatar_icon):
            st.markdown(msg["content"])
            if "sources" in msg and msg["sources"]:
                with st.expander("View Source References", expanded=False, icon=":material/menu_book:"):
                    for src in msg["sources"]:
                        st.markdown(f"""
                        <div class="source-card">
                            <span class="source-title">{src['file']} — Page {src['page']}</span> 
                            <span class="category-badge">{src.get('category', 'Other')}</span>
                            <div style="margin-top: 4px; font-size: 0.82rem; color: #9CA3AF;">Relevance Score: {src.get('relevance_score', 0):.2f}</div>
                            <div class="source-snippet">"{src['snippet']}"</div>
                        </div>
                        """, unsafe_allow_html=True)

    # 2. Unified Search & Retrieval Console Bar (Single-row at bottom)
    chunk_options = [2, 3, 4, 5, 6, 8, 10]
    default_k_idx = chunk_options.index(settings.TOP_K) if settings.TOP_K in chunk_options else 2

    with st.container(border=True, key="chat_unified_bar"):
        col_cat, col_input, col_k, col_clear = st.columns([1.8, 5.0, 1.7, 0.7], vertical_alignment="center")
        with col_cat:
            categories = ["All", "Academic", "IT", "Projects", "Policies", "Notices", "Guides", "FAQs", "Research", "Other"]
            selected_category = st.selectbox(
                "Category",
                categories,
                index=0,
                format_func=lambda c: "All Categories" if c == "All" else c,
                label_visibility="collapsed",
                help="Filter search to a specific document category"
            )
        with col_input:
            user_query = st.chat_input("Ask a question about your documents...")
        with col_k:
            top_k = st.selectbox(
                "Chunks",
                chunk_options,
                index=default_k_idx,
                format_func=lambda x: f"Top {x} Chunks",
                label_visibility="collapsed",
                help="Number of document excerpts/chunks retrieved to answer each question"
            )
        with col_clear:
            if st.button("", icon=":material/delete_sweep:", use_container_width=True, help="Clear conversation history"):
                st.session_state.messages = []
                st.rerun()

    # Bottom spacer so chat messages don't overlap unified bottom bar
    st.markdown('<div class="chat-bottom-spacer"></div>', unsafe_allow_html=True)
    st.markdown('<div class="chat-footer-hint"><svg style="width:14px;height:14px;fill:#6B7280;vertical-align:-2px;margin-right:6px;" viewBox="0 0 24 24"><path d="M11 7h2v2h-2zm0 4h2v6h-2zm1-9C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/></svg>For best results, ask specific questions related to your uploaded documents.</div>', unsafe_allow_html=True)

    if user_query:
        # Append User Message
        st.session_state.messages.append({"role": "user", "content": user_query})

        # Process Response & Append to Messages
        with st.spinner("Processing request & generating response..."):
            try:
                sid = st.session_state.session_id
                if backend_online:
                    payload = {
                        "question": user_query,
                        "category": None if selected_category == "All" else selected_category,
                        "top_k": top_k,
                        "provider": active_provider
                    }
                    headers = {"x-session-id": sid}
                    if active_key:
                        headers["x-api-key"] = active_key
                        headers["x-provider"] = active_provider

                    res = requests.post(f"{BACKEND_URL}/ask", json=payload, headers=headers, timeout=60)
                    if res.status_code == 200:
                        data = res.json()
                    else:
                        data = {"answer": f"Backend Error ({res.status_code}): {res.text}", "sources": [], "grounded": False}
                else:
                    data = direct_ask(
                        question=user_query,
                        category=selected_category,
                        top_k=top_k,
                        api_key=active_key,
                        provider=active_provider,
                        session_id=sid
                    )

                answer = data["answer"]
                sources = data.get("sources", [])
                is_grounded = data.get("grounded", True)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources if is_grounded else []
                })

            except Exception as e:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"An error occurred while answering your question: {str(e)}",
                    "sources": []
                })

        # Clean rerun to render all messages in top-to-bottom sequence
        st.rerun()


# ================= TAB 2: DOCUMENT MANAGEMENT =================
with tab_docs:
    sid = st.session_state.session_id

    # Upload Documents Card
    with st.container(border=True):
        st.markdown("""
        <div style="margin-bottom: 12px;">
            <div style="font-size: 1.12rem; font-weight: 700; color: #F9FAFB;">Upload Documents</div>
            <div style="font-size: 0.8rem; color: #9CA3AF; margin-top: 2px;">Ingest and index PDF files into your isolated private workspace.</div>
        </div>
        """, unsafe_allow_html=True)

        col_u1, col_u2 = st.columns([3, 1])
        with col_u1:
            uploaded_files = st.file_uploader(
                "Drag and drop PDF files here",
                type=["pdf"],
                accept_multiple_files=True,
                help="Max file size: 200MB per file • Supported format: PDF",
                label_visibility="collapsed"
            )
        with col_u2:
            upload_category = st.selectbox(
                "Category Tag",
                ["Academic", "IT", "Projects", "Policies", "Notices", "Guides", "FAQs", "Research", "Other"],
                index=8,
                help="Assign a category tag to organize your indexed documents"
            )

        if st.button("Process & Index Documents", type="primary", disabled=not uploaded_files, icon=":material/upload_file:"):
            with st.spinner("Extracting text, chunking & storing vectors in Chroma DB..."):
                try:
                    if backend_online:
                        files_payload = [("files", (f.name, f.getvalue(), "application/pdf")) for f in uploaded_files]
                        data_payload = {"category": upload_category}
                        headers = {"x-session-id": sid}
                        res = requests.post(f"{BACKEND_URL}/upload", files=files_payload, data=data_payload, headers=headers)
                        if res.status_code == 200:
                            st.success(f"Processed {len(uploaded_files)} document(s) successfully!", icon=":material/check_circle:")
                            st.rerun()
                        else:
                            try:
                                detail_msg = res.json().get("detail", res.text)
                            except Exception:
                                detail_msg = res.text
                            st.error(f"Failed to upload: {detail_msg}", icon=":material/error:")
                    else:
                        processed = direct_upload(uploaded_files, upload_category, session_id=sid)
                        st.success(f"Processed {len(processed)} document(s) successfully!", icon=":material/check_circle:")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error during upload & indexing: {str(e)}", icon=":material/error:")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Indexed Documents Table Block
    with st.container(border=True):
        col_th1, col_th2 = st.columns([4, 1], vertical_alignment="center")
        with col_th1:
            st.markdown(f"""
            <div style="margin-bottom: 8px;">
                <div style="font-size: 1.12rem; font-weight: 700; color: #F9FAFB;">Indexed Documents</div>
                <div style="font-size: 0.8rem; color: #9CA3AF; margin-top: 2px;">
                    Workspace: <code style="background-color: #1E293B; color: #60A5FA; padding: 2px 7px; border-radius: 4px; font-size: 0.78rem; border: 1px solid #334155;">{sid}</code>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_th2:
            if st.button("Refresh", icon=":material/refresh:", use_container_width=True):
                st.rerun()

        try:
            if backend_online:
                res = requests.get(f"{BACKEND_URL}/documents", headers={"x-session-id": sid})
                docs_list = res.json() if res.status_code == 200 else []
            else:
                docs_list = direct_list_docs(session_id=sid)
        except Exception as e:
            docs_list = []
            st.error(f"Could not load document list: {str(e)}", icon=":material/error:")

        if not docs_list:
            st.markdown("""
            <div style="text-align: center; padding: 36px 20px; background-color: #0F172A; border: 1px dashed #334155; border-radius: 8px; margin: 10px 0;">
                <div style="color: #64748B; margin-bottom: 6px;">
                    <svg style="width: 32px; height: 32px; fill: currentColor;" viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/></svg>
                </div>
                <div style="font-size: 0.92rem; font-weight: 600; color: #E2E8F0; margin-bottom: 4px;">No documents in this workspace yet</div>
                <div style="font-size: 0.78rem; color: #94A3B8;">Upload PDF files above to index them into your private vector store.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            col_widths = [0.6, 3.2, 1.4, 0.8, 0.8, 1.8, 0.8]

            # Table Header
            h_idx, h_name, h_cat, h_pages, h_chunks, h_time, h_act = st.columns(col_widths, vertical_alignment="center")
            h_idx.markdown('<div class="table-header-col">#</div>', unsafe_allow_html=True)
            h_name.markdown('<div class="table-header-col">Document Name</div>', unsafe_allow_html=True)
            h_cat.markdown('<div class="table-header-col">Category</div>', unsafe_allow_html=True)
            h_pages.markdown('<div class="table-header-col" style="text-align: center;">Pages</div>', unsafe_allow_html=True)
            h_chunks.markdown('<div class="table-header-col" style="text-align: center;">Chunks</div>', unsafe_allow_html=True)
            h_time.markdown('<div class="table-header-col">Uploaded</div>', unsafe_allow_html=True)
            h_act.markdown('<div class="table-header-col" style="text-align: center;">Action</div>', unsafe_allow_html=True)

            st.markdown('<div style="border-bottom: 1px solid #1F2937; margin-bottom: 6px;"></div>', unsafe_allow_html=True)

            # Table Data Rows
            for idx, doc in enumerate(docs_list, 1):
                doc_id = doc["document_id"]
                filename = doc["filename"]
                category = doc.get("category", "Other")
                chunks = doc.get("chunk_count", 0)
                pages = doc.get("total_pages", 1)
                timestamp = doc.get("upload_timestamp", "")[:16].replace("T", " ")
                cat_slug = category.lower().replace(" ", "-")

                r_idx, r_name, r_cat, r_pages, r_chunks, r_time, r_act = st.columns(col_widths, vertical_alignment="center")
                r_idx.markdown(f'<div class="table-cell-text" style="color: #64748B; font-weight: 600;">{idx}</div>', unsafe_allow_html=True)
                r_name.markdown(f'''
                <div class="table-cell-text" style="display: flex; align-items: center; gap: 7px; overflow: hidden;">
                    <svg style="width: 14px; height: 14px; fill: #60A5FA; flex-shrink: 0;" viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/></svg>
                    <span title="{filename}" style="font-weight: 500; color: #F1F5F9; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{filename}</span>
                </div>
                ''', unsafe_allow_html=True)
                r_cat.markdown(f'<span class="category-pill cat-{cat_slug}">{category}</span>', unsafe_allow_html=True)
                r_pages.markdown(f'<div class="table-cell-text" style="text-align: center; color: #CBD5E1;">{pages}</div>', unsafe_allow_html=True)
                r_chunks.markdown(f'<div class="table-cell-text" style="text-align: center; color: #CBD5E1;">{chunks}</div>', unsafe_allow_html=True)
                r_time.markdown(f'<div class="table-cell-text" style="color: #94A3B8; font-size: 0.78rem;">{timestamp if timestamp else "Recent"}</div>', unsafe_allow_html=True)

                with r_act:
                    st.markdown('<div class="doc-row-del">', unsafe_allow_html=True)
                    if st.button("", icon=":material/delete:", key=f"del_{doc_id}", help=f"Delete {filename}"):
                        with st.spinner(f"Deleting {filename}..."):
                            if backend_online:
                                requests.delete(f"{BACKEND_URL}/documents/{doc_id}", headers={"x-session-id": sid})
                            else:
                                direct_delete_doc(doc_id, session_id=sid)
                            st.success(f"Deleted {filename}", icon=":material/check_circle:")
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)


# ================= TAB 3: HOW TO USE? =================
with tab_guide:
    st.markdown("""
    <div style="font-size: 1.25rem; font-weight: 700; color: #F9FAFB; margin-bottom: 3px;">Getting Started & User Guide</div>
    <div style="font-size: 0.88rem; color: #9CA3AF; margin-bottom: 18px;">A comprehensive walkthrough for configuring, querying, and managing your ContextIQ knowledge base.</div>
    """, unsafe_allow_html=True)

    col_g1, col_g2, col_g3 = st.columns(3)

    with col_g1:
        with st.container(border=True):
            st.markdown("""
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                <span style="background-color: #1E3A8A; color: #93C5FD; font-size: 0.76rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; letter-spacing: 0.04em;">STEP 1</span>
                <span style="font-size: 0.95rem; font-weight: 600; color: #F1F5F9;">Configure API Key</span>
            </div>
            <div style="font-size: 0.84rem; color: #9CA3AF; line-height: 1.6;">
                Open the left sidebar and enter your <b>Groq</b> or <b>OpenAI</b> API key. Keys persist securely in your browser session. Free Groq keys are available at <a href="https://console.groq.com/keys" target="_blank" style="color: #60A5FA; text-decoration: none;">console.groq.com</a>.
            </div>
            """, unsafe_allow_html=True)

    with col_g2:
        with st.container(border=True):
            st.markdown("""
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                <span style="background-color: #1E3A8A; color: #93C5FD; font-size: 0.76rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; letter-spacing: 0.04em;">STEP 2</span>
                <span style="font-size: 0.95rem; font-weight: 600; color: #F1F5F9;">Upload Documents</span>
            </div>
            <div style="font-size: 0.84rem; color: #9CA3AF; line-height: 1.6;">
                Navigate to the <b>Document Management</b> tab. Drag and drop PDF files (resumes, job descriptions, manuals, research), choose a category tag, and click <b>Process & Index Documents</b>.
            </div>
            """, unsafe_allow_html=True)

    with col_g3:
        with st.container(border=True):
            st.markdown("""
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                <span style="background-color: #1E3A8A; color: #93C5FD; font-size: 0.76rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; letter-spacing: 0.04em;">STEP 3</span>
                <span style="font-size: 0.95rem; font-weight: 600; color: #F1F5F9;">Ask the Assistant</span>
            </div>
            <div style="font-size: 0.84rem; color: #9CA3AF; line-height: 1.6;">
                Switch to <b>Ask Assistant</b>. Ask natural language questions in the bottom console bar. ContextIQ retrieves relevant chunks and generates grounded answers with exact source citations.
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    col_info1, col_info2 = st.columns(2)

    with col_info1:
        with st.container(border=True):
            st.markdown("""
            <div style="font-size: 0.96rem; font-weight: 600; color: #F1F5F9; margin-bottom: 10px;">Search Bar Controls & Settings</div>
            <div style="font-size: 0.85rem; color: #9CA3AF; line-height: 1.65;">
                <b style="color: #60A5FA;">Category Selector (Left):</b><br>
                Restricts retrieval to a specific document category (e.g. <i>Academic</i>, <i>Policies</i>, <i>IT</i>). To compare across multiple documents (e.g., comparing your resume with a job description), select <b>All Categories</b> to enable automatic multi-document retrieval.<br><br>
                <b style="color: #60A5FA;">Top Chunks (Right):</b><br>
                Controls how many text excerpts (chunks) are extracted from your documents to ground the answer. Each chunk contains a relevant passage with exact page citations. Choose <b>Top 2–4 Chunks</b> for focused Q&A, or <b>Top 6–10 Chunks</b> for comprehensive multi-document comparisons.<br><br>
                <b style="color: #60A5FA;">Clear Chat Button (🗑):</b><br>
                Clears conversation history to start a new inquiry with a clean slate.
            </div>
            """, unsafe_allow_html=True)

    with col_info2:
        with st.container(border=True):
            st.markdown("""
            <div style="font-size: 0.96rem; font-weight: 600; color: #F1F5F9; margin-bottom: 10px;">Recommended Query Patterns & Privacy</div>
            <div style="font-size: 0.85rem; color: #9CA3AF; line-height: 1.65;">
                <b style="color: #D1D5DB;">Resume & Alignment Inquiries:</b><br>
                • "Summarize my resume and professional background"<br>
                • "Is the shared job description aligns with my resume?"<br><br>
                <b style="color: #D1D5DB;">Comparative & Cross-Document Analysis:</b><br>
                • "What are the key differences between the two policies?"<br>
                • "Does the candidate have the qualifications needed for this role?"<br><br>
                <b style="color: #D1D5DB;">Privacy & On-Premise Embeddings:</b><br>
                • Your workspace is 100% private to your session ID.<br>
                • Vector embeddings run locally on your machine via HuggingFace (no document data sent to external embedding APIs).
            </div>
            """, unsafe_allow_html=True)
