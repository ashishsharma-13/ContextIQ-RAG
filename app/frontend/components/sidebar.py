"""Sidebar component for ContextIQ Streamlit frontend."""

import uuid
import streamlit as st
from app.config import settings


def render_sidebar(
    logo_data_url: str,
    active_provider: str,
    active_model_name: str,
    active_key: str,
    typed_key: str,
    backend_online: bool,
    vector_stats: dict
):
    """Renders the left sidebar containing brand header, model cards, keys, workspace session, and stats."""
    with st.sidebar:
        # Sidebar Header Brand with Enlarged Logo
        if logo_data_url:
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 16px;">
                <img src="{logo_data_url}" style="width: 58px; height: 58px; border-radius: 14px; object-fit: cover; border: 1px solid #374151; box-shadow: 0 4px 14px rgba(0,0,0,0.35);">
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
