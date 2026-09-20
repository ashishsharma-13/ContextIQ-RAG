import os
import sys
from pathlib import Path
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import settings
from app.frontend.styles import apply_custom_styles
from app.frontend.utils import get_base64_image, init_session_state, check_backend_health
from app.frontend.components.sidebar import render_sidebar
from app.frontend.components.chat_tab import render_chat_tab
from app.frontend.components.docs_tab import render_docs_tab
from app.frontend.components.guide_tab import render_guide_tab

LOGO_PATH = ROOT_DIR / "app" / "frontend" / "assets" / "logo.jpg"
LOGO_DATA_URL = get_base64_image(LOGO_PATH)
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# Page Configuration
st.set_page_config(
    page_title="ContextIQ - Personal Knowledge Assistant",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply sleek CSS theme
apply_custom_styles()

# Initialize session state
init_session_state()

# Resolve provider & API key
env_groq_key = settings.get_groq_api_key()
env_openai_key = settings.get_openai_api_key()
typed_key = st.session_state.user_api_key.strip()
choice = st.session_state.provider_choice

if choice == "OpenAI":
    active_provider = "openai"
    active_key = typed_key or env_openai_key
elif choice == "Groq":
    active_provider = "groq"
    active_key = typed_key or env_groq_key
else:  # Auto-detect
    if typed_key:
        active_provider = settings.detect_provider(key=typed_key)
        active_key = typed_key
    elif env_groq_key:
        active_provider = "groq"
        active_key = env_groq_key
    elif env_openai_key:
        active_provider = "openai"
        active_key = env_openai_key
    else:
        active_provider = settings.LLM_PROVIDER
        active_key = ""

active_model_name = settings.OPENAI_MODEL if active_provider == "openai" else settings.GROQ_MODEL

# Check backend status
backend_online, vector_stats = check_backend_health(BACKEND_URL, st.session_state.session_id)

# Render Sidebar
render_sidebar(
    logo_data_url=LOGO_DATA_URL,
    active_provider=active_provider,
    active_model_name=active_model_name,
    active_key=active_key,
    typed_key=typed_key,
    backend_online=backend_online,
    vector_stats=vector_stats
)

# Main Area Header
if LOGO_DATA_URL:
    st.markdown(f"""
    <div class="header-container">
        <div style="background-color: #1F2937; border: 1px solid #374151; border-radius: 16px; padding: 6px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
            <img src="{LOGO_DATA_URL}" style="width: 64px; height: 64px; border-radius: 12px; object-fit: cover;">
        </div>
        <div>
            <div class="main-title">ContextIQ</div>
            <div class="main-subtitle">Context-Aware Personal Knowledge Assistant</div>
            <div class="main-desc">Upload your documents and ask natural language questions with exact page citations.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="header-container">
        <div class="header-icon-box">
            <svg style="width:32px;height:32px;fill:#FFFFFF;" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>
        </div>
        <div>
            <div class="main-title">ContextIQ</div>
            <div class="main-subtitle">Context-Aware Personal Knowledge Assistant</div>
            <div class="main-desc">Upload your documents and ask natural language questions with exact page citations.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Navigation Tabs
tab_chat, tab_docs, tab_guide = st.tabs(["Ask Assistant", "Document Management", "How to Use?"])

assistant_avatar = str(LOGO_PATH) if LOGO_PATH.exists() else ":material/smart_toy:"

with tab_chat:
    render_chat_tab(
        backend_url=BACKEND_URL,
        backend_online=backend_online,
        active_provider=active_provider,
        active_key=active_key,
        assistant_avatar=assistant_avatar
    )

with tab_docs:
    render_docs_tab(backend_url=BACKEND_URL, backend_online=backend_online)

with tab_guide:
    render_guide_tab()
