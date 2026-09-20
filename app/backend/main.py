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
    description="Context-Aware Personal Knowledge Assistant RAG API (Groq LLaMA 120B + Local HuggingFace Embeddings)",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _get_clean_api_key(header_key: Optional[str]) -> Optional[str]:
    """Cleans header API key and returns None if empty so server .env key is used."""
    if header_key and header_key.strip():
        return header_key.strip()
    return None


class AskRequest(BaseModel):
    question: str = Field(..., description="Natural language question")
    category: Optional[str] = Field(None, description="Optional document category filter")
    top_k: Optional[int] = Field(None, description="Number of top chunks to retrieve")


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


class UploadResponse(BaseModel):
    message: str
    documents: List[DocumentSummary]


@app.get("/", tags=["Root"])
def root():
    """ContextIQ API Root Endpoint."""
    return {
        "message": "Welcome to ContextIQ API",
        "description": "Context-Aware Personal Knowledge Assistant (Powered by Groq 120B & Local HuggingFace)",
        "embedding_provider": "HuggingFace (sentence-transformers/all-MiniLM-L6-v2 - 100% Free Local)",
        "llm_engine": f"Groq ({settings.GROQ_MODEL})",
        "docs_url": "/docs",
        "health_url": "/health",
        "documents_url": "/documents"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Returns application health and vector store stats."""
    try:
        stats = get_vectorstore_stats()
        return {
            "status": "healthy",
            "llm_engine": f"Groq ({settings.GROQ_MODEL})",
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
    category: str = Form("Other")
):
    """
    Uploads and processes PDF files into ChromaDB using local HuggingFace embeddings.
    No API key is required for document indexing!
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files were provided for upload."
        )

    processed_summaries: List[DocumentSummary] = []
    batch_filenames = set()

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file.filename}. ContextIQ currently supports PDF files."
            )

        fn_lower = file.filename.lower()
        if fn_lower in batch_filenames or is_document_already_indexed(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Document '{file.filename}' is already uploaded and indexed. Please delete the existing file before re-uploading."
            )
        batch_filenames.add(fn_lower)

        doc_id = str(uuid.uuid4())
        safe_filename = f"{doc_id}_{file.filename}"
        save_path = Path(settings.DOCUMENTS_DIR) / safe_filename

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

            chunks = split_documents(docs)
            add_chunks_to_vectorstore(chunks)

            summary = DocumentSummary(
                document_id=doc_id,
                filename=file.filename,
                file_path=str(save_path),
                category=category,
                upload_timestamp=docs[0].metadata.get("upload_timestamp", "") if docs else "",
                total_pages=docs[0].metadata.get("total_pages", 1) if docs else 1,
                chunk_count=len(chunks)
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
    x_api_key: Optional[str] = Header(None)
):
    """
    Submits a question and returns a grounded answer with source citations.
    """
    if not request.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty."
        )

    api_key = _get_clean_api_key(x_api_key)

    try:
        result = ask_question(
            question=request.question,
            category_filter=request.category,
            top_k=request.top_k,
            api_key=api_key
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
def list_documents():
    """
    Returns a list of all currently indexed documents and metadata.
    """
    try:
        docs = get_indexed_documents()
        return [DocumentSummary(**d) for d in docs]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching documents: {str(e)}"
        )


@app.delete("/documents/{document_id}", tags=["Document Management"])
def delete_document(document_id: str):
    """
    Deletes all chunks of a document from Chroma DB and removes the raw file from disk.
    """
    try:
        docs = get_indexed_documents()
        target_doc = next((d for d in docs if d["document_id"] == document_id), None)

        deleted_chunks = delete_document_by_id(document_id)

        if target_doc and target_doc.get("file_path"):
            raw_path = Path(target_doc["file_path"])
            if raw_path.exists():
                os.remove(raw_path)

        return {
            "message": f"Successfully deleted document '{document_id}'.",
            "deleted_chunks": deleted_chunks
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting document {document_id}: {str(e)}"
        )
