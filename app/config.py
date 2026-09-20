import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
FALLBACK_ENV = BASE_DIR.parent / ".env"

if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE, override=True)
elif FALLBACK_ENV.exists():
    load_dotenv(dotenv_path=FALLBACK_ENV, override=True)
else:
    load_dotenv(override=True)


def _get_streamlit_secret(key_name: str) -> str:
    """Safely retrieves a key from streamlit secrets if running inside Streamlit."""
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key_name in st.secrets:
            val = st.secrets[key_name]
            return str(val).strip() if val else ""
    except Exception:
        pass
    return ""


class Settings(BaseSettings):
    # Supported Providers: Groq, OpenAI
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "groq")

    # Groq Settings
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

    # OpenAI Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.0"))

    # Local Embeddings (Free, No API key needed)
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # RAG & Chunking Parameters
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    TOP_K: int = int(os.getenv("TOP_K", "4"))
    # Adjusted threshold: 0.15 ensures valid queries like resumes are not dropped
    SIMILARITY_SCORE_THRESHOLD: float = float(os.getenv("SIMILARITY_SCORE_THRESHOLD", "0.15"))
    
    # Storage Paths
    CHROMA_PERSIST_DIR: str = str(BASE_DIR / os.getenv("CHROMA_PERSIST_DIR", "chroma_db"))
    DOCUMENTS_DIR: str = str(BASE_DIR / os.getenv("DOCUMENTS_DIR", "documents"))

    def get_groq_api_key(self) -> str:
        """Returns active Groq API key from env, settings, or streamlit secrets."""
        key = os.getenv("GROQ_API_KEY") or self.GROQ_API_KEY
        if not key:
            key = _get_streamlit_secret("GROQ_API_KEY")
        if not key and ENV_FILE.exists():
            load_dotenv(dotenv_path=ENV_FILE, override=True)
            key = os.getenv("GROQ_API_KEY", "")
        return key.strip()

    def get_openai_api_key(self) -> str:
        """Returns active OpenAI API key from env, settings, or streamlit secrets."""
        key = os.getenv("OPENAI_API_KEY") or self.OPENAI_API_KEY
        if not key:
            key = _get_streamlit_secret("OPENAI_API_KEY")
        if not key and ENV_FILE.exists():
            load_dotenv(dotenv_path=ENV_FILE, override=True)
            key = os.getenv("OPENAI_API_KEY", "")
        return key.strip()

    def detect_provider(self, key: Optional[str] = None, explicit_provider: Optional[str] = None) -> str:
        """Detects whether Groq or OpenAI should be used based on key prefix or preference."""
        if explicit_provider and explicit_provider.lower() in ["groq", "openai"]:
            return explicit_provider.lower()
        if key:
            k = key.strip()
            if k.startswith("sk-"):
                return "openai"
            if k.startswith("gsk_"):
                return "groq"
        # If no key provided, check available configured keys
        if self.get_groq_api_key():
            return "groq"
        if self.get_openai_api_key():
            return "openai"
        return self.LLM_PROVIDER.lower()

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }


settings = Settings()

Path(settings.CHROMA_PERSIST_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.DOCUMENTS_DIR).mkdir(parents=True, exist_ok=True)
