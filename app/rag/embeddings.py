from typing import Optional
from langchain_core.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings
from app.config import settings

# Global cached embedding model instance for fast reuse
_embedding_model_instance: Optional[Embeddings] = None


def get_embedding_function(api_key: Optional[str] = None, allow_dummy: bool = False) -> Embeddings:
    """
    Returns an instance of HuggingFaceEmbeddings using sentence-transformers/all-MiniLM-L6-v2.
    This runs 100% locally with zero cost, zero API keys, and zero rate limits.
    """
    global _embedding_model_instance
    if _embedding_model_instance is None:
        _embedding_model_instance = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
    return _embedding_model_instance
