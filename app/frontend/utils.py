"""Utility functions and session initialization for ContextIQ frontend."""

import base64
import uuid
from pathlib import Path
import requests
import streamlit as st


def get_base64_image(image_path: Path) -> str:
    """Convert image file to base64 data URI for inline HTML rendering."""
    if image_path.exists():
        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            return f"data:image/jpeg;base64,{encoded}"
    return ""


def init_session_state():
    """Initializes default Streamlit session state variables."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())[:8]

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "user_api_key" not in st.session_state:
        st.session_state.user_api_key = ""

    if "provider_choice" not in st.session_state:
        st.session_state.provider_choice = "Auto-detect"


def check_backend_health(backend_url: str, session_id: str):
    """Checks if FastAPI backend is online and retrieves vector store stats."""
    try:
        res = requests.get(f"{backend_url}/health", headers={"x-session-id": session_id}, timeout=2)
        if res.status_code == 200:
            return True, res.json().get("vector_store", {})
    except Exception:
        pass
    return False, {}
