import os
import shutil
import uuid
from typing import List, Optional
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.config import settings
from app.rag.loader import load_pdf_document
from app.rag.splitter import split_documents
from app.rag.vectorstore import (
    add_chunks_to_vectorstore,
    delete_document_by_id,
    get_indexed_documents,
    get_vectorstore_stats,
    is_document_already_indexed
)
from app.rag.chain import ask_question


app = FastAPI(
    title="ContextIQ Backend API",
    description="Context-Aware Personal Knowledge Assistant RAG API (Groq & OpenAI + Local HuggingFace Embeddings + Session Privacy)",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _get_clean_header(header_val: Optional[str]) -> Optional[str]:
    """Cleans header value and returns None if empty."""
    if header_val and header_val.strip():
        return header_val.strip()
    return None


class AskRequest(BaseModel):
    question: str = Field(..., description="Natural language question")
    category: Optional[str] = Field(None, description="Optional document category filter")
    top_k: Optional[int] = Field(None, description="Number of top chunks to retrieve")
    provider: Optional[str] = Field(None, description="Optional LLM provider ('groq' or 'openai')")


class SourceReference(BaseModel):
    file: str
    page: int
    category: str
    document_id: str
    snippet: str
    relevance_score: float


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceReference]
    grounded: bool


class DocumentSummary(BaseModel):
    document_id: str
    filename: str
    file_path: str
    category: str
    upload_timestamp: str
    total_pages: int
    chunk_count: int
    session_id: Optional[str] = ""


class UploadResponse(BaseModel):
    message: str
    documents: List[DocumentSummary]


@app.get("/", tags=["Root"])
def root():
    """ContextIQ API Root Endpoint."""
    return {
        "message": "Welcome to ContextIQ API",
        "description": "Context-Aware Personal Knowledge Assistant (Powered by Groq/OpenAI & Local HuggingFace)",
        "embedding_provider": "HuggingFace (sentence-transformers/all-MiniLM-L6-v2 - 100% Free Local)",
        "supported_engines": ["Groq", "OpenAI"],
        "docs_url": "/docs",
        "health_url": "/health",
        "documents_url": "/documents"
    }


@app.get("/health", tags=["Health"])
def health_check(x_session_id: Optional[str] = Header(None)):
    """Returns application health and vector store stats."""
    try:
        session_id = _get_clean_header(x_session_id)
        stats = get_vectorstore_stats(session_id=session_id)
        return {
            "status": "healthy",
            "llm_engine": f"{settings.LLM_PROVIDER.capitalize()}",
            "vector_store": stats
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e)
        }


@app.post("/upload", response_model=UploadResponse, tags=["Document Processing"])
async def upload_documents(
    files: List[UploadFile] = File(...),
    category: str = Form("Other"),
    x_session_id: Optional[str] = Header(None)
):
    """
    Uploads and processes PDF files into ChromaDB using local HuggingFace embeddings.
    Isolates documents per session_id for user privacy.
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files were provided for upload."
        )

    session_id = _get_clean_header(x_session_id) or "default_session"
    session_dir = Path(settings.DOCUMENTS_DIR) / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    processed_summaries: List[DocumentSummary] = []
    batch_filenames = set()

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file.filename}. ContextIQ currently supports PDF files."
            )

        fn_lower = file.filename.lower()
        if fn_lower in batch_filenames or is_document_already_indexed(file.filename, session_id=session_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Document '{file.filename}' is already uploaded and indexed in your workspace."
            )
        batch_filenames.add(fn_lower)

        doc_id = str(uuid.uuid4())
        safe_filename = f"{doc_id}_{file.filename}"
        save_path = session_dir / safe_filename

        try:
            with open(save_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file {file.filename}: {str(e)}"
            )

        try:
            docs = load_pdf_document(
                file_path=str(save_path),
                document_id=doc_id,
                category=category
            )

            for d in docs:
                d.metadata["source"] = file.filename
                d.metadata["session_id"] = session_id

            chunks = split_documents(docs)
            add_chunks_to_vectorstore(chunks, session_id=session_id)

            summary = DocumentSummary(
                document_id=doc_id,
                filename=file.filename,
                file_path=str(save_path),
                category=category,
                upload_timestamp=docs[0].metadata.get("upload_timestamp", "") if docs else "",
                total_pages=docs[0].metadata.get("total_pages", 1) if docs else 1,
                chunk_count=len(chunks),
                session_id=session_id
            )
            processed_summaries.append(summary)

        except Exception as e:
            if save_path.exists():
                os.remove(save_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing document {file.filename}: {str(e)}"
            )

    return UploadResponse(
        message=f"Successfully processed {len(processed_summaries)} document(s).",
        documents=processed_summaries
    )


@app.post("/ask", response_model=AskResponse, tags=["RAG Question Answering"])
def ask(
    request: AskRequest,
    x_api_key: Optional[str] = Header(None),
    x_session_id: Optional[str] = Header(None),
    x_provider: Optional[str] = Header(None)
):
    """
    Submits a question and returns a grounded answer with source citations.
    Isolates context to the caller's session_id.
    """
    if not request.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty."
        )

    api_key = _get_clean_header(x_api_key)
    session_id = _get_clean_header(x_session_id)
    provider = _get_clean_header(x_provider) or request.provider

    try:
        result = ask_question(
            question=request.question,
            category_filter=request.category,
            top_k=request.top_k,
            api_key=api_key,
            provider=provider,
            session_id=session_id
        )
        return AskResponse(**result)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing RAG query: {str(e)}"
        )


@app.get("/documents", response_model=List[DocumentSummary], tags=["Document Management"])
def list_documents(x_session_id: Optional[str] = Header(None)):
    """
    Returns a list of indexed documents isolated to the caller's session_id.
    """
    try:
        session_id = _get_clean_header(x_session_id)
        docs = get_indexed_documents(session_id=session_id)
        return [DocumentSummary(**d) for d in docs]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching documents: {str(e)}"
        )


@app.delete("/documents/{document_id}", tags=["Document Management"])
def delete_document(
    document_id: str,
    x_session_id: Optional[str] = Header(None)
):
    """
    Deletes all chunks of a document belonging to the caller's session and removes the raw file.
    """
    try:
        session_id = _get_clean_header(x_session_id)
        docs = get_indexed_documents(session_id=session_id)
        target_doc = next((d for d in docs if d["document_id"] == document_id), None)

        if not target_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document '{document_id}' not found in your session."
            )

        deleted_chunks = delete_document_by_id(document_id, session_id=session_id)

        if target_doc.get("file_path"):
            raw_path = Path(target_doc["file_path"])
            if raw_path.exists():
                os.remove(raw_path)

        return {
            "message": f"Successfully deleted document '{document_id}'.",
            "deleted_chunks": deleted_chunks
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting document {document_id}: {str(e)}"
        )
