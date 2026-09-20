"""Document management tab component for ContextIQ Streamlit frontend."""

from pathlib import Path
import streamlit as st
import requests
from app.frontend.direct_client import direct_upload, direct_list_docs, direct_delete_doc


def render_docs_tab(backend_url: str, backend_online: bool):
    """Renders the Document Management interface: upload card and indexed documents table."""
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
                        res = requests.post(f"{backend_url}/upload", files=files_payload, data=data_payload, headers=headers)
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
                res = requests.get(f"{backend_url}/documents", headers={"x-session-id": sid})
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
                                requests.delete(f"{backend_url}/documents/{doc_id}", headers={"x-session-id": sid})
                            else:
                                direct_delete_doc(doc_id, session_id=sid)
                            st.success(f"Deleted {filename}", icon=":material/check_circle:")
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
