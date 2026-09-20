import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from langchain_core.documents import Document
from pypdf import PdfReader


def load_pdf_document(
    file_path: str,
    document_id: Optional[str] = None,
    category: str = "Other"
) -> List[Document]:
    """
    Loads a PDF document and extracts content into LangChain Document objects.
    Each document corresponds to a single page and retains rich metadata.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    doc_id = document_id or str(uuid.uuid4())
    upload_time = datetime.now(timezone.utc).isoformat()
    filename = path.name

    reader = PdfReader(file_path)
    documents = []

    for idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = text.strip()

        # Skip completely empty pages
        if not text:
            continue

        metadata = {
            "source": filename,
            "file_path": str(path.resolve()),
            "page": idx + 1,  # 1-based page numbering for user readability
            "document_id": doc_id,
            "category": category,
            "upload_timestamp": upload_time,
            "total_pages": len(reader.pages)
        }

        doc = Document(page_content=text, metadata=metadata)
        documents.append(doc)

    return documents
