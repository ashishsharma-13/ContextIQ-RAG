from typing import List, Tuple, Optional, Dict, Any
from langchain_core.documents import Document
from app.config import settings
from app.rag.vectorstore import get_vectorstore


def retrieve_relevant_chunks(
    query: str,
    top_k: Optional[int] = None,
    category_filter: Optional[str] = None,
    score_threshold: Optional[float] = None,
    api_key: Optional[str] = None
) -> List[Tuple[Document, float]]:
    """
    Retrieves document chunks relevant to the query from Chroma DB with distance scores.
    Optionally filters by document category and relevance score threshold.
    """
    vectorstore = get_vectorstore(api_key)
    k = top_k or settings.TOP_K

    filter_dict: Optional[Dict[str, Any]] = None
    if category_filter and category_filter.lower() != "all":
        filter_dict = {"category": category_filter}

    # Execute similarity search with distance score
    results = vectorstore.similarity_search_with_score(
        query=query,
        k=k,
        filter=filter_dict
    )

    # Filter out results if a similarity score threshold is set
    # Note: In ChromaDB default (L2 distance or Cosine distance), lower distance means higher similarity.
    threshold = score_threshold if score_threshold is not None else settings.SIMILARITY_SCORE_THRESHOLD
    
    filtered_results = []
    for doc, score in results:
        # Chroma score is distance. If distance <= 1.2 (for cosine/L2), it's relevant.
        # We can also convert distance to approximate relevance score.
        relevance_score = max(0.0, 1.0 - (score / 2.0))
        
        # Attach normalized relevance score to doc metadata
        doc.metadata["relevance_score"] = round(relevance_score, 4)
        doc.metadata["distance"] = round(float(score), 4)

        if relevance_score >= threshold:
            filtered_results.append((doc, score))

    return filtered_results
