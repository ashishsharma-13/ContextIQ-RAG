from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from langchain_chroma import Chroma
from app.config import settings
from app.rag.embeddings import get_embedding_function


COLLECTION_NAME = "contextiq_hf_documents"


def get_vectorstore(api_key: Optional[str] = None, allow_dummy_embeddings: bool = False) -> Chroma:
    """
    Initializes and returns the persistent Chroma vector store with local HuggingFace embeddings.
    """
    embedding_func = get_embedding_function()
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embedding_func,
        persist_directory=settings.CHROMA_PERSIST_DIR
    )


def add_chunks_to_vectorstore(
    chunks: List[Document],
    api_key: Optional[str] = None,
    session_id: Optional[str] = None
) -> List[str]:
    """
    Adds document chunks to Chroma vector store, tagging them with session_id for privacy.
    Returns list of generated vector IDs.
    """
    if not chunks:
        return []

    if session_id:
        clean_sid = str(session_id).strip()
        for chunk in chunks:
            chunk.metadata["session_id"] = clean_sid

    vectorstore = get_vectorstore(api_key)
    ids = [chunk.metadata.get("chunk_id", None) for chunk in chunks]
    
    if any(i is None for i in ids):
        ids = None

    return vectorstore.add_documents(chunks, ids=ids)


def delete_document_by_id(
    document_id: str,
    api_key: Optional[str] = None,
    session_id: Optional[str] = None
) -> int:
    """
    Deletes all chunks associated with a specific document_id from Chroma store.
    If session_id is provided, ensures only the session's document is deleted.
    Returns the count of deleted chunks.
    """
    vectorstore = get_vectorstore(api_key)
    collection = vectorstore._collection

    if session_id:
        clean_sid = str(session_id).strip()
        result = collection.get(where={"$and": [{"document_id": document_id}, {"session_id": clean_sid}]})
    else:
        result = collection.get(where={"document_id": document_id})

    matching_ids = result.get("ids", [])

    if matching_ids:
        collection.delete(ids=matching_ids)
        return len(matching_ids)

    return 0


def get_indexed_documents(
    api_key: Optional[str] = None,
    session_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Aggregates metadata of all indexed documents in Chroma store.
    If session_id is provided, only returns documents belonging to that session.
    Returns a list of dicts with document summary info.
    """
    vectorstore = get_vectorstore(api_key)
    collection = vectorstore._collection

    if session_id:
        clean_sid = str(session_id).strip()
        result = collection.get(where={"session_id": clean_sid}, include=["metadatas"])
    else:
        result = collection.get(include=["metadatas"])

    metadatas = result.get("metadatas", []) or []
    docs_map: Dict[str, Dict[str, Any]] = {}

    for meta in metadatas:
        if not meta:
            continue
        
        doc_id = meta.get("document_id")
        if not doc_id:
            continue

        if doc_id not in docs_map:
            docs_map[doc_id] = {
                "document_id": doc_id,
                "filename": meta.get("source", "Unknown"),
                "file_path": meta.get("file_path", ""),
                "category": meta.get("category", "Other"),
                "upload_timestamp": meta.get("upload_timestamp", ""),
                "total_pages": meta.get("total_pages", 1),
                "session_id": meta.get("session_id", ""),
                "chunk_count": 0
            }

        docs_map[doc_id]["chunk_count"] += 1

    return list(docs_map.values())


def get_vectorstore_stats(
    api_key: Optional[str] = None,
    session_id: Optional[str] = None
) -> Dict[str, int]:
    """
    Returns statistics about the vector store, scoped to session_id if provided.
    """
    documents = get_indexed_documents(api_key=api_key, session_id=session_id)
    total_chunks = sum(d.get("chunk_count", 0) for d in documents)
    
    return {
        "total_chunks": total_chunks,
        "total_documents": len(documents)
    }


def is_document_already_indexed(
    filename: str,
    api_key: Optional[str] = None,
    session_id: Optional[str] = None
) -> bool:
    """
    Checks if a document with the given filename is already indexed in Chroma vector store
    for the specified session (or globally if session_id is None).
    Matches filename case-insensitively.
    """
    if not filename:
        return False
    indexed = get_indexed_documents(api_key=api_key, session_id=session_id)
    target = filename.strip().lower()
    return any(doc.get("filename", "").strip().lower() == target for doc in indexed)
