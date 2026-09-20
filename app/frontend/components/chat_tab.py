"""Chat tab component for ContextIQ Streamlit frontend."""

from pathlib import Path
import streamlit as st
import requests
from app.config import settings
from app.frontend.direct_client import direct_ask


def render_chat_tab(
    backend_url: str,
    backend_online: bool,
    active_provider: str,
    active_key: str,
    assistant_avatar: str
):
    """Renders the Ask Assistant chat interface, source references, and unified bottom dock."""
    # 1. Render all chat messages chronologically from TOP to BOTTOM
    if not st.session_state.messages:
        with st.chat_message("assistant", avatar=assistant_avatar):
            st.markdown(
                "Hello! I am **ContextIQ**, your personal context-aware knowledge assistant. "
                "Ask me a question about your uploaded documents."
            )

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

    with st.container(key="chat_unified_bar"):
        col_cat, col_input, col_k, col_clear = st.columns([1.7, 5.2, 1.7, 0.6], vertical_alignment="center")
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

    # Footer guidance hint positioned cleanly below the dock bar
    st.markdown(
        '<div class="chat-footer-hint">'
        '<svg style="width:13px;height:13px;fill:#64748B;flex-shrink:0;" viewBox="0 0 24 24">'
        '<path d="M11 7h2v2h-2zm0 4h2v6h-2zm1-9C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>'
        '</svg> For best results, ask specific questions related to your uploaded documents.</div>',
        unsafe_allow_html=True
    )

    # Bottom spacer so chat messages scroll safely above the dock
    st.markdown('<div class="chat-bottom-spacer"></div>', unsafe_allow_html=True)

    # 3. Handle submitted user query
    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})

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

                    res = requests.post(f"{backend_url}/ask", json=payload, headers=headers, timeout=60)
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

        st.rerun()
