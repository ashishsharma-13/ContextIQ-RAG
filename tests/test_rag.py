import os
from pathlib import Path
import pytest
from pypdf import PdfWriter
from langchain_core.documents import Document

from app.rag.loader import load_pdf_document
from app.rag.splitter import split_documents
from app.rag.prompts import INSUFFICIENT_CONTEXT_RESPONSE, get_rag_prompt_template
from app.rag.chain import format_context, extract_source_references


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


def test_is_document_already_indexed():
    """Tests checking if a document is already indexed."""
    from app.rag.vectorstore import is_document_already_indexed
    assert is_document_already_indexed("") is False
    assert is_document_already_indexed("non_existent_file_xyz123.pdf") is False

