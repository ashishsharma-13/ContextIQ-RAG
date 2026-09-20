import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR.parent / ".env"

if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE, override=True)
else:
    load_dotenv(override=True)


class Settings(BaseSettings):
    # Sole Provider: Groq
    LLM_PROVIDER: str = "groq"
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.0"))

    # Local Embeddings (Free, No API key needed)
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # RAG & Chunking Parameters
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    TOP_K: int = int(os.getenv("TOP_K", "4"))
    SIMILARITY_SCORE_THRESHOLD: float = float(os.getenv("SIMILARITY_SCORE_THRESHOLD", "0.3"))
    
    # Storage Paths
    CHROMA_PERSIST_DIR: str = str(BASE_DIR / os.getenv("CHROMA_PERSIST_DIR", "chroma_db"))
    DOCUMENTS_DIR: str = str(BASE_DIR / os.getenv("DOCUMENTS_DIR", "documents"))

    def get_groq_api_key(self) -> str:
        """Returns active Groq API key from env or settings."""
        key = os.getenv("GROQ_API_KEY") or self.GROQ_API_KEY
        if not key and ENV_FILE.exists():
            load_dotenv(dotenv_path=ENV_FILE, override=True)
            key = os.getenv("GROQ_API_KEY", "")
        return key.strip()

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }


settings = Settings()

Path(settings.CHROMA_PERSIST_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.DOCUMENTS_DIR).mkdir(parents=True, exist_ok=True)
