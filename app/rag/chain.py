import re
from typing import Dict, Any, Optional, List
from langchain_core.output_parsers import StrOutputParser
from app.config import settings
from app.rag.retriever import retrieve_relevant_chunks
from app.rag.prompts import (
    get_rag_prompt_template,
    INSUFFICIENT_CONTEXT_RESPONSE,
    is_greeting_query,
    get_greeting_response
)


def get_llm(api_key: Optional[str] = None):
    """
    Initializes ChatGroq using the configured Groq API key and model.
    """
    key = (api_key and api_key.strip()) or settings.get_groq_api_key()
    if not key:
        raise ValueError(
            "Groq API Key is missing. Please set GROQ_API_KEY in your .env file or sidebar."
        )
    from langchain_groq import ChatGroq
    return ChatGroq(
        model=settings.GROQ_MODEL,
        groq_api_key=key,
        temperature=settings.TEMPERATURE
    )


def sanitize_llm_output(text: str) -> str:
    """
    Removes raw citation annotations like 【3†L1-L4】 or [1†source] emitted by certain models.
    """
    # Remove bracketed annotations like 【3†L1-L4】
    cleaned = re.sub(r'【.*?】', '', text)
    # Remove bracketed source markers like [1†source]
    cleaned = re.sub(r'\[\d+†.*?\]', '', cleaned)
    # Remove multiple whitespace before punctuation
    cleaned = re.sub(r'\s+([.,;:!?])', r'\1', cleaned)
    return cleaned.strip()


def format_context(chunk_tuples) -> str:
    """
    Formats retrieved document chunks into a structured context string for the prompt.
    """
    formatted_blocks = []
    for idx, (doc, score) in enumerate(chunk_tuples, 1):
        source = doc.metadata.get("source", "Unknown Document")
        page = doc.metadata.get("page", 1)
        category = doc.metadata.get("category", "Other")
        content = doc.page_content.strip()

        block = f"--- Document Chunk [{idx}] ---\nSource: {source} (Page {page}, Category: {category})\nContent:\n{content}"
        formatted_blocks.append(block)

    return "\n\n".join(formatted_blocks)


def extract_source_references(chunk_tuples) -> List[Dict[str, Any]]:
    """
    Deduplicates and extracts source attribution metadata from retrieved document chunks.
    """
    seen_sources = set()
    sources = []

    for doc, score in chunk_tuples:
        source_file = doc.metadata.get("source", "Unknown Document")
        page = doc.metadata.get("page", 1)
        category = doc.metadata.get("category", "Other")
        doc_id = doc.metadata.get("document_id", "")
        relevance_score = doc.metadata.get("relevance_score", 0.0)

        source_key = (source_file, page)
        if source_key not in seen_sources:
            seen_sources.add(source_key)
            snippet = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            sources.append({
                "file": source_file,
                "page": page,
                "category": category,
                "document_id": doc_id,
                "snippet": snippet,
                "relevance_score": relevance_score
            })

    return sources


def ask_question(
    question: str,
    category_filter: Optional[str] = None,
    top_k: Optional[int] = None,
    api_key: Optional[str] = None,
    provider: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes the full RAG pipeline:
    1. Greeting intent check -> Returns conversational answer if greeting.
    2. Retrieval -> Relevancy check.
    3. Groq LLM Generation -> Output sanitization -> Source attribution.
    """
    cleaned_question = question.strip()

    # Step 1: Check if input is a general conversational greeting
    if is_greeting_query(cleaned_question):
        return {
            "question": cleaned_question,
            "answer": get_greeting_response(cleaned_question),
            "sources": [],
            "grounded": True
        }

    # Step 2: Retrieve relevant document chunks using local HuggingFace embeddings
    chunk_tuples = retrieve_relevant_chunks(
        query=cleaned_question,
        top_k=top_k,
        category_filter=category_filter
    )

    # Step 3: Handle cases where no relevant context was found
    if not chunk_tuples:
        return {
            "question": cleaned_question,
            "answer": INSUFFICIENT_CONTEXT_RESPONSE,
            "sources": [],
            "grounded": False
        }

    # Step 4: Format context & initialize Groq LLM
    context_text = format_context(chunk_tuples)
    prompt_template = get_rag_prompt_template()
    llm = get_llm(api_key=api_key)

    chain = prompt_template | llm | StrOutputParser()

    # Step 5: Invoke generation & sanitize output
    raw_answer = chain.invoke({
        "context": context_text,
        "question": cleaned_question
    })

    answer = sanitize_llm_output(raw_answer)

    # Step 6: Extract source citations
    sources = extract_source_references(chunk_tuples)
    is_grounded = INSUFFICIENT_CONTEXT_RESPONSE.lower() not in answer.lower()

    return {
        "question": cleaned_question,
        "answer": answer,
        "sources": sources if is_grounded else [],
        "grounded": is_grounded
    }
