# ContextIQ 🧠

### Context-Aware Personal Knowledge Assistant (RAG Document Intelligence)

ContextIQ is an enterprise-grade **Retrieval-Augmented Generation (RAG)** document intelligence system built with **Python**, **LangChain**, **Groq** & **OpenAI**, local **HuggingFace Embeddings**, **ChromaDB**, **FastAPI**, and **Streamlit**.

Instead of manually digging through scattered PDFs (academic papers, IT manuals, resumes, job descriptions, corporate policies, FAQs), ContextIQ creates a centralized, searchable knowledge layer. You can ask natural-language questions and receive grounded answers backed by traceable source page references, relevance scores, and multi-document comparative analysis.

---

## 🌟 Core Features

- **Dual LLM Provider Support (Groq & OpenAI)**:
  - Supports **Groq** (`llama-3.3-70b-versatile`) for ultra-fast, high-accuracy inference.
  - Supports **OpenAI** (`gpt-4o-mini`) as a secondary or primary provider.
  - Intelligent auto-detection of provider based on key prefix (`gsk_...` vs `sk-...`).
  - Seamless Streamlit Cloud Secrets integration (`st.secrets`).
- **100% Free Local Embeddings**:
  - Uses HuggingFace `sentence-transformers/all-MiniLM-L6-v2` locally — zero API costs for document indexing and zero external data leaks during embedding.
- **Multi-User Private Workspace Isolation**:
  - Every session generates a unique private **Workspace ID**.
  - Document storage on disk, ChromaDB vector collections, and API queries are strictly isolated per session. Users cannot see, query, or delete other users' documents.
- **Cross-Document Alignment & Comparative Retrieval**:
  - Detects cross-document comparative intent (e.g., *"Is the shared job description aligns with my resume?"*).
  - Automatically queries across multiple document categories and allocates balanced chunk quotas to ground side-by-side comparisons.
- **Resume & Self-Referential Query Answering**:
  - Calibrated similarity threshold (`0.15`) and query expansion specifically tuned for resumes, CVs, and candidate profiles.
- **Duplicate Protection**:
  - Automatically checks workspace vector store entries to prevent duplicate PDF uploads and chunk bloat.
- **Conversational Greetings**:
  - Gracefully handles conversational queries (`"hi"`, `"hello"`, `"who are you"`) with friendly assistant introductions.
- **Multi-Document Ingestion & Categorization**:
  - Upload multiple PDF files across categories (`Academic`, `IT`, `Projects`, `Policies`, `Research`, `Guides`, `FAQs`, `Notices`, `Other`).
- **Grounded Answer Generation & Exact Citations**:
  - Every response includes collapsible source reference cards featuring file name, exact 1-based page numbers, category badges, and relevance scores.
- **Modern Single-Row Search & Retrieval Dock Console**:
  - Unified bottom console featuring Category filter dropdown, natural language chat input with send arrow, Top Chunks selector (Top 2–10), and one-click Clear Chat button.
- **Modular Frontend Architecture**:
  - Clean separation of concerns with component-driven Streamlit architecture (`styles.py`, `direct_client.py`, `utils.py`, and `components/`).
- **RESTful FastAPI Backend**:
  - Complete REST API supporting `/upload`, `/ask`, `/documents`, `/documents/{document_id}`, and `/health` with session privacy headers.

---

## 🏗️ System Architecture

```text
                                  INDEXING PIPELINE
Documents (PDFs) ──> PyPDF Loader ──> Recursive Splitter ──> HuggingFace Embeddings ──> ChromaDB Vector Store
                                    (Chunk: 1000 / Ov: 200)   (all-MiniLM-L6-v2)     (Metadata: session_id,
                                                                                      category, source, page)

                                RETRIEVAL & GENERATION PIPELINE
User Query ──> Intent Detection ──> Dense Embedding ──> Chroma Similarity Search ──> Balanced Quotas
                   │                                                                      │
                   ├── Comparative Query? ──────────> Multi-Doc Proportional Chunks ──────┤
                   └── Greeting Query?    ──────────> Conversational Intro                │
                                                                                          ▼
Answer + Verifiable Citations <── LLM Inference <── Strict Grounding Prompt <── Merged Document Context
                             (Groq or OpenAI)
```

---

## 🛠️ Project Structure

```text
ContextIQ-RAG/
├── app/
│   ├── config.py                 # Centralized Pydantic settings, secrets & environment config
│   ├── backend/
│   │   └── main.py               # FastAPI REST endpoints (/upload, /ask, /documents, /health)
│   ├── frontend/
│   │   ├── streamlit_app.py      # Lightweight main orchestrator entrypoint (< 110 lines)
│   │   ├── styles.py             # Complete CSS design system, responsive rules & theme tokens
│   │   ├── utils.py              # Asset loaders, session ID helpers & backend health checker
│   │   ├── direct_client.py      # Direct Python RAG fallback routines when backend is offline
│   │   ├── components/
│   │   │   ├── __init__.py
│   │   │   ├── sidebar.py        # Sidebar brand header, model card, key inputs & workspace manager
│   │   │   ├── chat_tab.py       # Tab 1: Chat conversation flow, citations & unified search console
│   │   │   ├── docs_tab.py       # Tab 2: Document upload card & workspace document table
│   │   │   └── guide_tab.py      # Tab 3: "How to Use?" user manual & controls guide
│   │   └── assets/
│   │       └── logo.jpg          # ContextIQ project logo asset
│   └── rag/
│       ├── loader.py             # PyPDF loader with metadata extraction
│       ├── splitter.py           # Recursive text chunking with metadata preservation
│       ├── embeddings.py         # Local HuggingFace sentence-transformers embedding wrapper
│       ├── vectorstore.py        # Persistent Chroma collection manager & session privacy filters
│       ├── retriever.py          # Balanced multi-document retrieval & query expansion
│       ├── prompts.py            # Strict grounding, comparative & greeting prompts
│       └── chain.py              # Multi-provider LCEL RAG chain (Groq & OpenAI support)
├── .streamlit/
│   └── config.toml               # Streamlit server configuration (polling watcher, headless)
├── documents/                   # Local storage for session-isolated uploaded PDF files
├── chroma_db/                   # Persistent Chroma vector database storage
├── tests/
│   ├── test_rag.py              # RAG pipeline unit tests (chunking, expansion, multi-doc)
│   └── test_api.py              # FastAPI integration tests (session isolation, upload, ask)
├── .env.example                 # Example environment variables
├── requirements.txt             # Project dependencies
└── README.md                    # Project documentation
```

---

## ⚡ Quick Start & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/ashishsharma-13/ContextIQ-RAG.git
cd ContextIQ-RAG
```

### 2. Environment Configuration

Create a `.env` file in the project root:

```env
# Central LLM Configuration (Groq or OpenAI)
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Optional OpenAI Fallback
OPENAI_API_KEY=sk-your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Provider Selection: "groq" or "openai"
LLM_PROVIDER=groq

# Retrieval Defaults
TOP_K=4
CHROMA_PERSIST_DIR=./chroma_db
DOCUMENTS_DIR=./documents
```

> **Note**: You can also paste your API key directly into the Streamlit sidebar at runtime. Keys are stored securely in your browser session.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Application

### Option A: Run FastAPI + Streamlit (Recommended Architecture)

1. **Start the FastAPI Backend**:
   ```bash
   python -m uvicorn app.backend.main:app --reload --port 8000
   ```
   *Interactive Swagger API Docs available at `http://127.0.0.1:8000/docs`.*

2. **Start the Streamlit Frontend** (in a separate terminal):
   ```bash
   streamlit run app/frontend/streamlit_app.py
   ```
   *Opens in your browser at `http://localhost:8501`.*

### Option B: Standalone Direct Python Mode

If the FastAPI backend is not running, ContextIQ automatically switches to **Direct Python Engine Mode** and processes embeddings, retrieval, and LLM chains in-process without requiring the API server.

---

## 📖 How to Use

### 1. Configure Your API Key
Open the left sidebar and enter your **Groq** (`gsk_...`) or **OpenAI** (`sk-...`) API key.
- Get a free Groq API key in seconds at [console.groq.com/keys](https://console.groq.com/keys).
- When deployed on Streamlit Cloud, keys can also be configured in `secrets.toml`.

### 2. Upload & Categorize Documents
1. Navigate to the **Document Management** tab.
2. Drag and drop one or more PDF files (resumes, job specifications, course notes, manuals, research).
3. Select an appropriate category tag (`Academic`, `IT`, `Projects`, `Policies`, `Research`, etc.).
4. Click **Process & Index Documents**.
5. Your files will be indexed into your private vector store and displayed in the document table with page count, chunk metrics, and delete options.

### 3. Ask the Assistant
1. Switch to the **Ask Assistant** tab.
2. Use the unified bottom search console:
   - **Category Filter (Left)**: Restrict search to a specific category or choose **All Categories** for multi-document cross-comparisons.
   - **Search Input (Center)**: Type your question in natural language.
   - **Top Chunks (Right)**: Adjust context depth:
     - **Top 2–4 Chunks**: Ideal for quick, focused questions.
     - **Top 6–10 Chunks**: Best for comprehensive cross-document alignment (e.g., comparing a resume with a job description).
   - **Clear Chat (🗑)**: Reset conversation history.
3. Every grounded answer includes expandable **Source Reference** cards citing file names, exact 1-based page numbers, relevance scores, and matching excerpts.

---

## 🧪 Automated Testing

ContextIQ includes an automated test suite verifying API contracts, session isolation, provider detection, query expansion, and cross-document balanced retrieval:

```bash
pytest -v tests/
```

Test coverage includes:
- `test_health_endpoint`: Backend health and Chroma DB connectivity.
- `test_health_endpoint_with_session`: Session-scoped metric reporting.
- `test_documents_endpoint`: Document listing and category assignment.
- `test_session_isolation_in_vectorstore`: Multi-user workspace boundary verification.
- `test_is_greeting_query_resume_protection`: Greeting classifier accuracy without triggering false positives on resumes.
- `test_query_expansion_for_resumes`: Retrieval optimization for candidate profile queries.
- `test_comparative_query_detection`: Comparative intent recognition.
- `test_comparative_multi_document_retrieval`: Balanced chunk allocation across multi-category documents.

---

## 📡 REST API Reference

All endpoints accept the `X-Session-ID` header to isolate workspace data.

| Method | Endpoint | Description | Headers |
|---|---|---|---|
| `GET` | `/health` | Server health status & session vector stats | `X-Session-ID` *(optional)* |
| `POST` | `/upload` | Ingest and index PDF files into ChromaDB | `X-Session-ID` *(optional)*, `multipart/form-data` |
| `POST` | `/ask` | Submit question & receive grounded answer + citations | `X-Session-ID`, `X-API-Key` *(optional)*, `X-Provider` *(optional)* |
| `GET` | `/documents` | List indexed documents for the active workspace | `X-Session-ID` *(optional)* |
| `DELETE` | `/documents/{id}` | Delete document chunks from vector store and disk | `X-Session-ID` *(optional)* |

Interactive OpenAPI documentation and live request testing is available at `http://127.0.0.1:8000/docs`.

---

## 📄 License

This project is licensed under the MIT License.
