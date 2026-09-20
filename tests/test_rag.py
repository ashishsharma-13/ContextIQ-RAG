import os
from pathlib import Path
import pytest
from langchain_core.documents import Document

from app.config import settings
from app.rag.loader import load_pdf_document
from app.rag.splitter import split_documents
from app.rag.prompts import (
    INSUFFICIENT_CONTEXT_RESPONSE,
    get_rag_prompt_template,
    is_greeting_query
)
from app.rag.chain import format_context, extract_source_references
from app.rag.retriever import (
    expand_query_if_needed,
    retrieve_relevant_chunks,
    is_comparative_query
)
from app.rag.vectorstore import (
    add_chunks_to_vectorstore,
    get_indexed_documents,
    is_document_already_indexed,
    delete_document_by_id
)


def test_splitter_chunking():
    """Tests recursive text splitting while retaining metadata."""
    doc = Document(
        page_content="A " * 600,
        metadata={"source": "test.pdf", "page": 1, "document_id": "test-123"}
    )
    chunks = split_documents([doc], chunk_size=500, chunk_overlap=50)

    assert len(chunks) > 1
    for idx, chunk in enumerate(chunks):
        assert chunk.metadata["source"] == "test.pdf"
        assert chunk.metadata["document_id"] == "test-123"
        assert chunk.metadata["chunk_index"] == idx


def test_prompt_template():
    """Tests prompt template rendering."""
    template = get_rag_prompt_template()
    formatted = template.format(context="Test Context", question="What is DNS?")
    
    assert "ContextIQ" in formatted
    assert "Test Context" in formatted
    assert "What is DNS?" in formatted
    assert "RESUME / PERSONAL QUERIES" in formatted


def test_format_context():
    """Tests formatting of retrieved document chunks into context blocks."""
    doc1 = Document(
        page_content="DNS translates domain names to IP addresses.",
        metadata={"source": "Network.pdf", "page": 1, "category": "IT"}
    )
    doc2 = Document(
        page_content="Systemd resolves DNS queries locally.",
        metadata={"source": "Linux.pdf", "page": 5, "category": "IT"}
    )

    tuples = [(doc1, 0.2), (doc2, 0.3)]
    formatted = format_context(tuples)

    assert "Source: Network.pdf (Page 1" in formatted
    assert "DNS translates domain names" in formatted
    assert "Source: Linux.pdf (Page 5" in formatted


def test_extract_source_references():
    """Tests deduplication and extraction of source citations."""
    doc1 = Document(
        page_content="DNS translates domain names to IP addresses.",
        metadata={"source": "Network.pdf", "page": 1, "category": "IT", "document_id": "doc-1", "relevance_score": 0.9}
    )
    doc2 = Document(
        page_content="Additional DNS info.",
        metadata={"source": "Network.pdf", "page": 1, "category": "IT", "document_id": "doc-1", "relevance_score": 0.85}
    )
    doc3 = Document(
        page_content="Linux networking commands.",
        metadata={"source": "Linux.pdf", "page": 8, "category": "IT", "document_id": "doc-2", "relevance_score": 0.75}
    )

    sources = extract_source_references([(doc1, 0.2), (doc2, 0.3), (doc3, 0.5)])

    assert len(sources) == 2
    assert sources[0]["file"] == "Network.pdf"
    assert sources[0]["page"] == 1
    assert sources[1]["file"] == "Linux.pdf"
    assert sources[1]["page"] == 8


def test_provider_detection():
    """Tests detecting OpenAI vs Groq providers from key prefixes."""
    assert settings.detect_provider(key="sk-proj-1234567890abcdef") == "openai"
    assert settings.detect_provider(key="gsk_1234567890abcdef") == "groq"
    assert settings.detect_provider(explicit_provider="OpenAI") == "openai"
    assert settings.detect_provider(explicit_provider="Groq") == "groq"


def test_is_greeting_query_resume_protection():
    """Tests that resume and personal queries are NOT flagged as conversational greetings."""
    assert is_greeting_query("hello") is True
    assert is_greeting_query("hi there") is True
    assert is_greeting_query("tell me about me") is False
    assert is_greeting_query("tell me about me / resume") is False
    assert is_greeting_query("who am I") is False
    assert is_greeting_query("summarize my resume") is False


def test_query_expansion_for_resumes():
    """Tests query expansion when searching personal/resume questions."""
    orig = "tell me about me / resume"
    expanded = expand_query_if_needed(orig)
    assert "resume" in expanded
    assert "candidate" in expanded
    assert "education" in expanded
    assert "skills" in expanded

    # Normal query should not be modified
    assert expand_query_if_needed("What is a subnet mask?") == "What is a subnet mask?"


def test_session_isolation_in_vectorstore():
    """Tests that documents indexed under session A are not visible or duplicate-checked in session B."""
    import uuid
    sid_a = f"test_user_a_{uuid.uuid4().hex[:6]}"
    sid_b = f"test_user_b_{uuid.uuid4().hex[:6]}"

    doc_a = Document(
        page_content="Resume content of User A: Python, FastAPI.",
        metadata={
            "source": "My_Resume.pdf",
            "page": 1,
            "category": "Projects",
            "document_id": f"doc_{sid_a}",
            "chunk_id": f"chunk_{sid_a}_1"
        }
    )

    add_chunks_to_vectorstore([doc_a], session_id=sid_a)

    # Session A should see the document
    assert is_document_already_indexed("My_Resume.pdf", session_id=sid_a) is True
    docs_a = get_indexed_documents(session_id=sid_a)
    assert any(d["filename"] == "My_Resume.pdf" for d in docs_a)

    # Session B should NOT see the document
    assert is_document_already_indexed("My_Resume.pdf", session_id=sid_b) is False
    docs_b = get_indexed_documents(session_id=sid_b)
    assert not any(d["filename"] == "My_Resume.pdf" for d in docs_b)

    # Cleanup
    delete_document_by_id(f"doc_{sid_a}", session_id=sid_a)
    assert is_document_already_indexed("My_Resume.pdf", session_id=sid_a) is False


def test_comparative_query_detection():
    """Tests detection of comparative, alignment, and multi-document queries."""
    # Alignment and matching
    assert is_comparative_query("Is the shared job description aligns with my resume?") is True
    assert is_comparative_query("Does the job description align with my resume?") is True
    assert is_comparative_query("Does my resume match the job requirements?") is True
    assert is_comparative_query("Is my background suitable for this role?") is True
    assert is_comparative_query("Compare both documents") is True
    assert is_comparative_query("What are the differences between document A and document B?") is True

    # Single-document or non-comparative queries should be False
    assert is_comparative_query("tell me about me / resume") is False
    assert is_comparative_query("who am I") is False
    assert is_comparative_query("What is DNS?") is False
    assert is_comparative_query("What is a subnet mask?") is False


def test_comparative_multi_document_retrieval():
    """Tests that a comparative query retrieves chunks from all relevant documents across categories."""
    import uuid
    sid = f"test_comp_{uuid.uuid4().hex[:6]}"

    doc1 = Document(
        page_content="IT Communications and Training Specialist role at UoH. Responsible for digital training and staff workshops.",
        metadata={
            "source": "IT_Job_Description.pdf",
            "page": 1,
            "category": "Policies",
            "document_id": f"doc1_{sid}",
            "chunk_id": f"chunk_jd_{sid}"
        }
    )
    doc2 = Document(
        page_content="Ashish Sharma. Full Stack Developer with experience in technical workshops, training, and documentation.",
        metadata={
            "source": "Ashish_Resume.pdf",
            "page": 1,
            "category": "Academic",
            "document_id": f"doc2_{sid}",
            "chunk_id": f"chunk_res_{sid}"
        }
    )

    add_chunks_to_vectorstore([doc1, doc2], session_id=sid)

    # Query asking for alignment between both documents
    query = "Is the shared job description aligns with my resume?"
    chunks = retrieve_relevant_chunks(query, session_id=sid, top_k=4)

    sources = {c[0].metadata["source"] for c in chunks}
    assert "IT_Job_Description.pdf" in sources
    assert "Ashish_Resume.pdf" in sources

    # Cleanup
    delete_document_by_id(f"doc1_{sid}", session_id=sid)
    delete_document_by_id(f"doc2_{sid}", session_id=sid)

