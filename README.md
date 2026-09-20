# ContextIQ 🧠

### Context-Aware Personal Knowledge Assistant (RAG Document Intelligence)

ContextIQ is a high-performance **Retrieval-Augmented Generation (RAG)** document intelligence system built with **Python**, **LangChain**, **Groq (LLaMA 120B)**, local **HuggingFace Embeddings**, **ChromaDB**, **FastAPI**, and **Streamlit**.

Instead of manually digging through scattered PDFs (academic notes, IT manuals, project requirements, FAQs), ContextIQ creates a centralized, searchable knowledge layer. You can ask natural-language questions and receive grounded answers backed by traceable source page references.

---

## 🌟 Core Features

- **Groq LLaMA-3 Engine**: Powered exclusively by Groq (`openai/gpt-oss-120b`) for ultra-fast, high-accuracy RAG inference.
- **100% Free Local Embeddings**: Uses HuggingFace `sentence-transformers/all-MiniLM-L6-v2` locally — zero API costs for document indexing!
- **Duplicate Protection**: Automatically checks existing vector store entries to prevent duplicate PDF uploads and chunk bloat.
- **Conversational Greetings**: Gracefully handles general queries (`"hi"`, `"hello"`, `"who are you"`) with friendly responses instead of retrieval errors.
- **Multi-Document Ingestion**: Upload multiple PDF files across categories (`Academic`, `IT`, `Projects`, `Policies`, `Research`, `Guides`, etc.).
- **Rich Metadata Extraction**: Tracks file name, page numbers (1-based), document IDs (UUID), category tags, and upload timestamps.
- **Persistent Vector Storage**: Uses ChromaDB to store document chunks and embeddings locally in `./chroma_db`.
- **Grounded Answer Generation**: Strictly grounds LLM answers in retrieved context to minimize hallucinations.
- **Source Citation Cards**: Every grounded response includes exact file and page citations (`📄 Network_Notes.pdf — Page 12`).
- **RESTful FastAPI Backend**: Complete API for `/upload`, `/ask`, `/documents`, `/documents/{document_id}`, and `/health`.
- **Polished Streamlit UI**: Custom dark theme with project logo branding, Streamlit Material icons, fixed bottom search input, centered hint caption, and real-time metric cards.

---

## 🏗️ System Architecture

```text
                  INDEXING PIPELINE
Documents (PDFs) ──> PyPDF Loader ──> Recursive Text Splitter ──> HuggingFace Embeddings ──> ChromaDB Store
                                                                (all-MiniLM-L6-v2)

                  RETRIEVAL & GENERATION PIPELINE
User Question ──> Local Query Embedding ──> Chroma Retriever ──> Grounded RAG Prompt ──> Groq LLM (LLaMA 120B) ──> Answer + Citations
```

---

## 🛠️ Project Structure

```text
c:\RAG_ContextIQ\
├── app/
│   ├── config.py             # Centralized Pydantic settings & environment configuration
│   ├── backend/
│   │   └── main.py           # FastAPI REST endpoints (/upload, /ask, /documents, /health)
│   ├── frontend/
│   │   ├── streamlit_app.py  # Streamlit UI with dark theme, logo branding & Material icons
│   │   └── assets/
│   │       └── logo.jpg      # ContextIQ project logo asset
│   └── rag/
│       ├── loader.py         # PyPDF loader with metadata extraction
│       ├── splitter.py       # Recursive text chunking with metadata preservation
│       ├── embeddings.py     # Local HuggingFace sentence-transformers embedding wrapper
│       ├── vectorstore.py    # Persistent Chroma collection manager & duplicate checker
│       ├── retriever.py      # Top-K & category-filtered similarity retrieval
│       ├── prompts.py        # Strict grounding & greeting prompts
│       └── chain.py          # End-to-end LCEL RAG chain & annotation sanitizer
├── documents/               # Local directory for uploaded raw PDF documents
├── chroma_db/               # Persistent Chroma vector database storage
├── tests/
│   ├── test_rag.py          # RAG pipeline unit tests
│   └── test_api.py          # FastAPI API endpoint integration tests
├── .env                     # Environment variable configuration (Groq API Key)
├── requirements.txt         # Project dependencies
└── README.md
```

---

## ⚡ Quick Start & Setup

### 1. Environment Configuration

Create a `.env` file in the project root and add your Groq API Key:

```env
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
TOP_K=4
CHROMA_PERSIST_DIR=./chroma_db
DOCUMENTS_DIR=./documents
```

*(Note: You can also enter your Groq API key directly in the Streamlit UI sidebar).*

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Application

### Option A: Run FastAPI + Streamlit (Recommended)

1. **Start the FastAPI Backend**:
   ```bash
   python -m uvicorn app.backend.main:app --reload --port 8000
   ```
   *Interactive API Docs available at `http://127.0.0.1:8000/docs`.*

2. **Start the Streamlit Frontend** (in a second terminal):
   ```bash
   streamlit run app/frontend/streamlit_app.py
   ```
   *Opens in your browser at `http://localhost:8501`.*

### Option B: Direct Python Standalone Mode

If the FastAPI backend server is offline, Streamlit automatically operates in **Direct Engine Mode** using the local Python modules directly.

---

## 🧪 Running Automated Tests

Run the complete test suite with `pytest`:

```bash
pytest -v tests/
```

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Application health status & vector DB document/chunk stats |
| `POST` | `/upload` | Ingest and index PDF files into ChromaDB (with duplicate checks) |
| `POST` | `/ask` | Submit a question & receive grounded response with page citations |
| `GET` | `/documents` | List all indexed documents with total page & chunk counts |
| `DELETE` | `/documents/{id}` | Delete document chunks from ChromaDB and disk |

---

## 📄 License
MIT License
