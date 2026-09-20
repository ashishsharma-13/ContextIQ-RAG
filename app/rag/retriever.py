import re
from typing import List, Tuple, Optional, Dict, Any
from langchain_core.documents import Document
from app.config import settings
from app.rag.vectorstore import get_vectorstore, get_indexed_documents


def is_comparative_query(query: str) -> bool:
    """
    Detects if a query is asking for comparison, alignment, fit, or cross-document analysis
    between multiple documents (e.g. resume vs job description, policies comparison, etc.).
    """
    q = query.lower()

    # Direct alignment/comparison verbs and nouns
    comp_patterns = [
        r"\baligns?\b", r"\baligned\b", r"\baligning\b", r"\balignment\b",
        r"\bmatches?\b", r"\bmatching\b",
        r"\bfits?\b", r"\bfitting\b", r"\bsuitable\b", r"\bsuitability\b",
        r"\bcompares?\b", r"\bcomparing\b", r"\bcomparison\b", r"\bcomparative\b",
        r"\bdifferences?\b", r"\bdiffer\b", r"\bdiffers\b",
        r"\bversus\b", r"\bvs\.?\b",
        r"\bboth\b", r"\bacross documents\b", r"\bacross the documents\b",
        r"\bbetween the documents\b", r"\bbetween both\b"
    ]
    if any(re.search(pat, q) for pat in comp_patterns):
        return True

    # Co-occurrence of candidate/personal terms and role/job/document terms
    personal_patterns = [
        r"\bresume\b", r"\bcv\b", r"\bprofile\b", r"\bbackground\b",
        r"\bexperience\b", r"\bmy skills\b", r"\bcandidate\b", r"\bme\b", r"\bmyself\b"
    ]
    target_patterns = [
        r"\bjob\b", r"\bdescription\b", r"\bjd\b", r"\brole\b", r"\bposition\b",
        r"\brequirements?\b", r"\bposting\b", r"\bassessment\b", r"\bvacancy\b", r"\bopportunity\b"
    ]
    has_personal = any(re.search(pat, q) for pat in personal_patterns)
    has_target = any(re.search(pat, q) for pat in target_patterns)
    if has_personal and has_target:
        return True

    return False


def expand_query_if_needed(query: str) -> str:
    """
    Expands self-referential or resume-related queries with relevant synonyms
    to bridge the semantic gap between first-person queries ('tell me about me')
    and third-person resume content ('Name, Education, Skills, Experience').
    For comparative queries (e.g. comparing resume to a job description),
    preserves query balance so both documents can be fairly retrieved.
    """
    if is_comparative_query(query):
        return query

    q_lower = query.lower()
    resume_keywords = [
        "resume", "cv", "about me", "who am i", "my profile",
        "my skills", "my experience", "my background", "my education",
        "my projects", "tell me about me", "tell me about myself"
    ]
    if any(kw in q_lower for kw in resume_keywords):
        return f"{query} resume CV candidate profile summary education skills experience projects background bio"
    return query


def retrieve_relevant_chunks(
    query: str,
    top_k: Optional[int] = None,
    category_filter: Optional[str] = None,
    score_threshold: Optional[float] = None,
    api_key: Optional[str] = None,
    session_id: Optional[str] = None
) -> List[Tuple[Document, float]]:
    """
    Retrieves document chunks relevant to the query from Chroma DB with distance scores.
    Enforces session isolation for privacy, supports category filtering,
    adaptive fallback, multi-document balanced retrieval, and self-referential query expansion.
    """
    vectorstore = get_vectorstore(api_key)
    k = top_k or settings.TOP_K
    threshold = score_threshold if score_threshold is not None else settings.SIMILARITY_SCORE_THRESHOLD

    has_sid = bool(session_id and session_id.strip())
    clean_sid = session_id.strip() if has_sid else None
    is_comp = is_comparative_query(query)

    # Fetch indexed documents in the active scope (session or global)
    try:
        indexed_docs = get_indexed_documents(api_key=api_key, session_id=clean_sid)
    except Exception:
        indexed_docs = []

    # CASE 1: MULTI-DOCUMENT BALANCED RETRIEVAL
    # When multiple documents exist and the query is comparative/alignment
    if len(indexed_docs) >= 2 and is_comp:
        balanced_results: List[Tuple[Document, float]] = []
        seen_chunk_ids = set()

        # Check relevance per document and gather candidate chunks
        relevant_doc_entries = []
        for doc_meta in indexed_docs:
            doc_id = doc_meta.get("document_id")
            if not doc_id:
                continue

            if has_sid:
                doc_filter = {
                    "$and": [
                        {"session_id": clean_sid},
                        {"document_id": doc_id}
                    ]
                }
            else:
                doc_filter = {"document_id": doc_id}

            try:
                # Probe document with the comparative query
                probe_chunks = vectorstore.similarity_search_with_score(
                    query=query,
                    k=max(3, k),
                    filter=doc_filter
                )
            except Exception:
                probe_chunks = []

            if probe_chunks:
                best_score = min(score for _, score in probe_chunks)
                # Keep document if its best chunk is within reasonable semantic distance
                if best_score <= 1.82:
                    relevant_doc_entries.append((doc_meta, probe_chunks))

        # If at least 2 documents are relevant, balance chunks across them
        if len(relevant_doc_entries) >= 2:
            num_docs = len(relevant_doc_entries)
            per_doc_k = max(2, (k + num_docs - 1) // num_docs)

            for doc_meta, probe_chunks in relevant_doc_entries:
                for doc, score in probe_chunks[:per_doc_k]:
                    cid = doc.metadata.get("chunk_id") or (
                        doc.metadata.get("source"),
                        doc.metadata.get("page"),
                        str(score)
                    )
                    if cid not in seen_chunk_ids and score <= 1.85:
                        seen_chunk_ids.add(cid)
                        relevance_score = max(0.0, 1.0 - (score / 2.0))
                        doc.metadata["relevance_score"] = round(relevance_score, 4)
                        doc.metadata["distance"] = round(float(score), 4)
                        balanced_results.append((doc, score))

            if balanced_results:
                return balanced_results

    # CASE 2: STANDARD RETRIEVAL PIPELINE
    search_query = expand_query_if_needed(query)
    has_cat = bool(category_filter and category_filter.lower() != "all" and not is_comp)

    if has_sid and has_cat:
        filter_dict = {
            "$and": [
                {"session_id": clean_sid},
                {"category": category_filter}
            ]
        }
    elif has_sid:
        filter_dict = {"session_id": clean_sid}
    elif has_cat:
        filter_dict = {"category": category_filter}
    else:
        filter_dict = None

    results = vectorstore.similarity_search_with_score(
        query=search_query,
        k=k,
        filter=filter_dict
    )

    filtered_results = []
    for doc, score in results:
        relevance_score = max(0.0, 1.0 - (score / 2.0))
        doc.metadata["relevance_score"] = round(relevance_score, 4)
        doc.metadata["distance"] = round(float(score), 4)

        if relevance_score >= threshold:
            filtered_results.append((doc, score))

    # Adaptive Fallback 1: If category filter was too restrictive and returned nothing,
    # fallback to searching without category restriction.
    if not filtered_results and has_cat:
        fallback_filter = {"session_id": clean_sid} if has_sid else None
        fallback_results = vectorstore.similarity_search_with_score(
            query=search_query,
            k=k,
            filter=fallback_filter
        )
        for doc, score in fallback_results:
            relevance_score = max(0.0, 1.0 - (score / 2.0))
            doc.metadata["relevance_score"] = round(relevance_score, 4)
            doc.metadata["distance"] = round(float(score), 4)
            if relevance_score >= threshold:
                filtered_results.append((doc, score))

    # Adaptive Fallback 2: If threshold filtered everything but candidates exist with distance <= 1.85,
    # return the top candidate chunks rather than completely failing.
    if not filtered_results and results:
        for doc, score in results[:k]:
            if score <= 1.85:
                filtered_results.append((doc, score))

    return filtered_results
