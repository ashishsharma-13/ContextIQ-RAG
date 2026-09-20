import os
import sys
import base64
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
        font-size: 1.6rem;
        font-weight: 800;
        color: #60A5FA;
        margin-bottom: 0px;
        line-height: 1.2;
    }
    .sidebar-brand-sub {
        font-size: 0.82rem;
        color: #9CA3AF;
        margin-bottom: 20px;
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

    /* Bottom Fixed Chat Input Bar Styling */
    [data-testid="stChatInput"] {
        position: fixed;
        bottom: 35px;
        left: calc(50% + 160px);
        transform: translateX(-50%);
        width: min(850px, 75%);
        z-index: 999;
        background-color: #111827;
        border: 1px solid #374151;
        border-radius: 16px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }
    .chat-bottom-spacer {
        height: 120px;
    }
    .chat-footer-hint {
        position: fixed;
        bottom: 8px;
        left: calc(50% + 160px);
        transform: translateX(-50%);
        z-index: 1000;
        font-size: 0.78rem;
        color: #6B7280;
        text-align: center;
        width: 100%;
        pointer-events: none;
    }
    </style>
""", unsafe_allow_html=True)


BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")


def check_backend_health():
    """Checks if FastAPI backend is online."""
    try:
        res = requests.get(f"{BACKEND_URL}/health", timeout=2)
        if res.status_code == 200:
            return True, res.json().get("vector_store", {})
    except Exception:
        pass
    return False, {}


# Direct Python Fallback functions
def direct_upload(files, category):
    from app.rag.loader import load_pdf_document
    from app.rag.splitter import split_documents
    from app.rag.vectorstore import add_chunks_to_vectorstore, is_document_already_indexed
    import uuid

    processed = []
    seen = set()
    for file in files:
        if file.name.lower() in seen or is_document_already_indexed(file.name):
            raise ValueError(f"Document '{file.name}' is already uploaded and indexed. Please delete the existing file before re-uploading.")
        seen.add(file.name.lower())

        doc_id = str(uuid.uuid4())
        safe_filename = f"{doc_id}_{file.name}"
        save_path = Path(settings.DOCUMENTS_DIR) / safe_filename
        with open(save_path, "wb") as f:
            f.write(file.getbuffer())

        docs = load_pdf_document(str(save_path), document_id=doc_id, category=category)
        for d in docs:
            d.metadata["source"] = file.name

        chunks = split_documents(docs)
        add_chunks_to_vectorstore(chunks)
        processed.append(file.name)
    return processed



def direct_ask(question, category, top_k, api_key):
    from app.rag.chain import ask_question
    cat_filter = None if category == "All" else category
    return ask_question(question, category_filter=cat_filter, top_k=top_k, api_key=api_key)


def direct_list_docs():
    from app.rag.vectorstore import get_indexed_documents
    return get_indexed_documents()


def direct_delete_doc(doc_id):
    from app.rag.vectorstore import delete_document_by_id, get_indexed_documents
    docs = get_indexed_documents()
    target = next((d for d in docs if d["document_id"] == doc_id), None)
    deleted_chunks = delete_document_by_id(doc_id)
    if target and target.get("file_path"):
        p = Path(target["file_path"])
        if p.exists():
            os.remove(p)
    return deleted_chunks


# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []


# ================= SIDEBAR UI =================
with st.sidebar:
    # Sidebar Header Brand with Logo
    if LOGO_DATA_URL:
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 14px;">
            <img src="{LOGO_DATA_URL}" style="width: 48px; height: 48px; border-radius: 12px; object-fit: cover; border: 1px solid #374151; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
            <div>
                <div class="sidebar-brand-title" style="font-size: 1.45rem; line-height: 1.1;">ContextIQ</div>
                <div class="sidebar-brand-sub" style="margin-bottom: 0; font-size: 0.78rem;">Knowledge Assistant</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="sidebar-brand-title">ContextIQ</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-brand-sub">Your Personal Knowledge Assistant</div>', unsafe_allow_html=True)

    st.divider()

    # Active Model Card
    st.markdown('<div class="sidebar-section-title">Model Architecture</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="model-info-card">
        <div class="model-name-title">
            <span><svg style="width:14px;height:14px;fill:#F59E0B;vertical-align:-2px;margin-right:4px;" viewBox="0 0 24 24"><path d="M7 2v11h3v9l7-12h-4l4-8z"/></svg> Engine:</span> Groq
        </div>
        <div class="model-detail-sub"><b>LLM:</b> {settings.GROQ_MODEL}</div>
        <div class="model-detail-sub"><b>Embeddings:</b> HuggingFace (all-MiniLM-L6-v2)</div>
    </div>
    """, unsafe_allow_html=True)

    groq_key = settings.get_groq_api_key()
    user_override_key = ""
    if groq_key:
        st.caption("Groq API Key: Active in .env")
    else:
        st.warning("No Groq Key found in .env", icon=":material/warning:")
        user_override_key = st.text_input("Enter Groq API Key", type="password")

    # System Status
    st.markdown('<div class="sidebar-section-title">System Status</div>', unsafe_allow_html=True)
    backend_online, vector_stats = check_backend_health()
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

    # Knowledge Base Metric Cards Side by Side
    st.markdown('<div class="sidebar-section-title">Knowledge Base</div>', unsafe_allow_html=True)
    if backend_online and vector_stats:
        total_docs = vector_stats.get("total_documents", 0)
        total_chunks = vector_stats.get("total_chunks", 0)
    else:
        from app.rag.vectorstore import get_vectorstore_stats
        try:
            stats = get_vectorstore_stats()
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
            <div class="metric-card-label">Documents</div>
        </div>
        """, unsafe_allow_html=True)
    with col_m2:
        st.markdown(f"""
        <div class="metric-card-box">
            <div style="color: #60A5FA; display: flex; justify-content: center; margin-bottom: 4px;">
                <svg style="width:22px;height:22px;fill:currentColor;" viewBox="0 0 24 24"><path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H8V4h12v12z"/></svg>
            </div>
            <div class="metric-card-num">{total_chunks}</div>
            <div class="metric-card-label">Chunks</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Retrieval Controls
    st.markdown('<div class="sidebar-section-title">Retrieval Controls</div>', unsafe_allow_html=True)
    top_k = st.slider("Top-K Chunks to Retrieve", min_value=1, max_value=10, value=settings.TOP_K)
    categories = ["All", "Academic", "IT", "Projects", "Policies", "Notices", "Guides", "FAQs", "Research", "Other"]
    selected_category = st.selectbox("Category Filter", categories)


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
tab_chat, tab_docs = st.tabs(["Ask Assistant", "Document Management"])


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

    # Bottom spacer so chat messages don't overlap fixed chat input bar
    st.markdown('<div class="chat-bottom-spacer"></div>', unsafe_allow_html=True)
    st.markdown('<div class="chat-footer-hint"><svg style="width:14px;height:14px;fill:#6B7280;vertical-align:-2px;margin-right:6px;" viewBox="0 0 24 24"><path d="M11 7h2v2h-2zm0 4h2v6h-2zm1-9C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/></svg>For best results, ask specific questions related to your uploaded documents.</div>', unsafe_allow_html=True)

    # 2. Chat Input fixed at bottom of page
    user_query = st.chat_input("Ask a question about your documents...")

    if user_query:
        # Append User Message
        st.session_state.messages.append({"role": "user", "content": user_query})

        # Process Response & Append to Messages
        with st.spinner("Processing request & generating response..."):
            try:
                active_key = user_override_key if user_override_key else None

                if backend_online:
                    payload = {
                        "question": user_query,
                        "category": None if selected_category == "All" else selected_category,
                        "top_k": top_k
                    }
                    headers = {"x-api-key": active_key} if active_key else {}
                    res = requests.post(f"{BACKEND_URL}/ask", json=payload, headers=headers, timeout=60)
                    if res.status_code == 200:
                        data = res.json()
                    else:
                        data = {"answer": f"Backend Error ({res.status_code}): {res.text}", "sources": [], "grounded": False}
                else:
                    data = direct_ask(user_query, selected_category, top_k, active_key)

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
    with st.container(border=True):
        st.markdown("### Upload Documents")
        st.caption("Add PDFs to your knowledge base. The documents will be processed, chunked, and indexed automatically.")

        col_u1, col_u2 = st.columns([3, 1])
        with col_u1:
            uploaded_files = st.file_uploader(
                "Drag and drop PDF files here",
                type=["pdf"],
                accept_multiple_files=True,
                help="Max file size: 200MB per file • Supported format: PDF"
            )
        with col_u2:
            upload_category = st.selectbox(
                "Category Tag",
                ["Academic", "IT", "Projects", "Policies", "Notices", "Guides", "FAQs", "Research", "Other"],
                index=8
            )

        if st.button("Process & Index Documents", type="primary", disabled=not uploaded_files, icon=":material/upload_file:"):
            with st.spinner("Extracting text, chunking & storing vectors in Chroma DB..."):
                try:
                    if backend_online:
                        files_payload = [("files", (f.name, f.getbuffer(), "application/pdf")) for f in uploaded_files]
                        data_payload = {"category": upload_category}
                        res = requests.post(f"{BACKEND_URL}/upload", files=files_payload, data=data_payload)
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
                        processed = direct_upload(uploaded_files, upload_category)
                        st.success(f"Processed {len(processed)} document(s) successfully!", icon=":material/check_circle:")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error during upload & indexing: {str(e)}", icon=":material/error:")

    st.divider()

    # Your Documents Table Block
    with st.container(border=True):
        col_th1, col_th2 = st.columns([4, 1])
        with col_th1:
            st.markdown("### Your Documents")
        with col_th2:
            if st.button("Refresh", icon=":material/refresh:"):
                st.rerun()

        try:
            if backend_online:
                res = requests.get(f"{BACKEND_URL}/documents")
                docs_list = res.json() if res.status_code == 200 else []
            else:
                docs_list = direct_list_docs()
        except Exception as e:
            docs_list = []
            st.error(f"Could not load document list: {str(e)}", icon=":material/error:")

        if not docs_list:
            st.info("No documents uploaded yet. Upload your PDF files above to start querying!", icon=":material/folder_open:")
        else:
            c_idx, c_name, c_cat, c_pages, c_chunks, c_time, c_act = st.columns([0.5, 3, 1.5, 1, 1, 2, 1])
            c_idx.markdown("**#**")
            c_name.markdown("**Filename**")
            c_cat.markdown("**Category**")
            c_pages.markdown("**Pages**")
            c_chunks.markdown("**Chunks**")
            c_time.markdown("**Uploaded On**")
            c_act.markdown("**Action**")

            st.divider()

            for idx, doc in enumerate(docs_list, 1):
                doc_id = doc["document_id"]
                filename = doc["filename"]
                category = doc.get("category", "Other")
                chunks = doc.get("chunk_count", 0)
                pages = doc.get("total_pages", 1)
                timestamp = doc.get("upload_timestamp", "")[:16].replace("T", " ")

                r_idx, r_name, r_cat, r_pages, r_chunks, r_time, r_act = st.columns([0.5, 3, 1.5, 1, 1, 2, 1])
                r_idx.write(str(idx))
                r_name.write(filename)
                r_cat.markdown(f'<span class="category-badge">{category}</span>', unsafe_allow_html=True)
                r_pages.write(str(pages))
                r_chunks.write(str(chunks))
                r_time.write(timestamp if timestamp else "Recent")
                if r_act.button("", icon=":material/delete:", key=f"del_{doc_id}", help="Delete document"):
                    with st.spinner(f"Deleting {filename}..."):
                        if backend_online:
                            requests.delete(f"{BACKEND_URL}/documents/{doc_id}")
                        else:
                            direct_delete_doc(doc_id)
                        st.success(f"Deleted {filename}", icon=":material/check_circle:")
                        st.rerun()
