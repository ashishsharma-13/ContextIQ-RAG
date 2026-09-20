from typing import List, Optional
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import settings


def split_documents(
    documents: List[Document],
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None
) -> List[Document]:
    """
    Splits a list of LangChain Document objects into smaller chunks
    while preserving original metadata on each chunk.
    """
    size = chunk_size or settings.CHUNK_SIZE
    overlap = chunk_overlap or settings.CHUNK_OVERLAP

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )

    chunks = splitter.split_documents(documents)
    
    # Add chunk index metadata for tracking sequential order
    for idx, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = f"{chunk.metadata.get('document_id', 'doc')}_{idx}"
        chunk.metadata["chunk_index"] = idx

    return chunks
