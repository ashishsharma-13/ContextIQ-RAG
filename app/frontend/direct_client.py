"""Direct Python RAG fallback routines for ContextIQ when backend is offline."""

import os
import uuid
from pathlib import Path
from app.config import settings


def direct_upload(files, category, session_id: str):
    """Uploads, parses, and indexes PDF files directly via local LangChain pipeline."""
    from app.rag.loader import load_pdf_document
    from app.rag.splitter import split_documents
    from app.rag.vectorstore import add_chunks_to_vectorstore, is_document_already_indexed

    session_dir = Path(settings.DOCUMENTS_DIR) / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    processed = []
    seen = set()
    for file in files:
        if file.name.lower() in seen or is_document_already_indexed(file.name, session_id=session_id):
            raise ValueError(
                f"Document '{file.name}' is already uploaded in your workspace. Please delete it before re-uploading."
            )
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


def direct_ask(question: str, category: str, top_k: int, api_key: str, provider: str, session_id: str):
    """Answers question directly using local retrieval and chat model."""
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
    """Lists indexed documents scoped to the active session."""
    from app.rag.vectorstore import get_indexed_documents
    return get_indexed_documents(session_id=session_id)


def direct_delete_doc(doc_id: str, session_id: str):
    """Deletes a document from the vector store and disk within the active session."""
    from app.rag.vectorstore import delete_document_by_id, get_indexed_documents
    docs = get_indexed_documents(session_id=session_id)
    target = next((d for d in docs if d["document_id"] == doc_id), None)
    deleted_chunks = delete_document_by_id(doc_id, session_id=session_id)
    if target and target.get("file_path"):
        p = Path(target["file_path"])
        if p.exists():
            try:
                os.remove(p)
            except OSError:
                pass
    return deleted_chunks
