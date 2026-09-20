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


def add_chunks_to_vectorstore(chunks: List[Document], api_key: Optional[str] = None) -> List[str]:
    """
    Adds document chunks to Chroma vector store.
    Returns list of generated vector IDs.
    """
    if not chunks:
        return []

    vectorstore = get_vectorstore(api_key)
    ids = [chunk.metadata.get("chunk_id", None) for chunk in chunks]
    
    if any(i is None for i in ids):
        ids = None

    return vectorstore.add_documents(chunks, ids=ids)


def delete_document_by_id(document_id: str, api_key: Optional[str] = None) -> int:
    """
    Deletes all chunks associated with a specific document_id from Chroma store.
    Returns the count of deleted chunks.
    """
    vectorstore = get_vectorstore(api_key)
    collection = vectorstore._collection

    result = collection.get(where={"document_id": document_id})
    matching_ids = result.get("ids", [])

    if matching_ids:
        collection.delete(ids=matching_ids)
        return len(matching_ids)

    return 0


def get_indexed_documents(api_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Aggregates metadata of all indexed documents in Chroma store.
    Returns a list of dicts with document summary info.
    """
    vectorstore = get_vectorstore(api_key)
    collection = vectorstore._collection

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
                "chunk_count": 0
            }

        docs_map[doc_id]["chunk_count"] += 1

    return list(docs_map.values())


def get_vectorstore_stats(api_key: Optional[str] = None) -> Dict[str, int]:
    """
    Returns high-level statistics about the vector store.
    """
    vectorstore = get_vectorstore(api_key)
    collection = vectorstore._collection
    
    total_chunks = collection.count()
    documents = get_indexed_documents(api_key)
    
    return {
        "total_chunks": total_chunks,
        "total_documents": len(documents)
    }


def is_document_already_indexed(filename: str, api_key: Optional[str] = None) -> bool:
    """
    Checks if a document with the given filename is already indexed in Chroma vector store.
    Matches filename case-insensitively.
    """
    if not filename:
        return False
    indexed = get_indexed_documents(api_key)
    target = filename.strip().lower()
    return any(doc.get("filename", "").strip().lower() == target for doc in indexed)

