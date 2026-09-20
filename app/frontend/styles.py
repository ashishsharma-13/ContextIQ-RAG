"""CSS styles and layout definitions for ContextIQ Streamlit frontend."""

CUSTOM_CSS = """
    <style>
    /* Global Page Styling */
    .stApp {
        background-color: #0B0F19;
        color: #F1F5F9;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    /* Reduce Streamlit Default Top Padding & Header Bar Height */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        height: 2rem !important;
    }
    /* Main Content Centering - Seamless on desktop, collapsed sidebar & mobile */
    [data-testid="stAppViewContainer"] {
        display: flex !important;
        width: 100vw !important;
        max-width: 100vw !important;
        overflow-x: hidden !important;
    }
    [data-testid="stAppViewContainer"] > div:not([data-testid="stSidebar"]) {
        flex: 1 1 auto !important;
        width: 100% !important;
        min-width: 0 !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
    }
    section[data-testid="stMain"],
    section.stMain,
    section.main {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        width: 100% !important;
        min-width: 0 !important;
    }
    .main .block-container,
    .stMainBlockContainer,
    [data-testid="stMainBlockContainer"],
    [data-testid="block-container"] {
        max-width: 900px !important;
        width: 100% !important;
        margin-left: auto !important;
        margin-right: auto !important;
        align-self: center !important;
        padding-top: 1rem !important;
        padding-bottom: 3rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        box-sizing: border-box !important;
    }
    [data-testid="stSidebarUserContent"] {
        padding-top: 1.2rem !important;
    }
    
    /* Sidebar Styling & Width Alignment - Seamless Collapse */
    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1F2937;
        transition: min-width 300ms cubic-bezier(0.4, 0, 0.2, 1),
                    max-width 300ms cubic-bezier(0.4, 0, 0.2, 1),
                    transform 300ms cubic-bezier(0.4, 0, 0.2, 1),
                    width 300ms cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    [data-testid="stSidebar"][aria-expanded="true"],
    .stApp:not(:has([data-testid="stSidebarCollapsedControl"])) [data-testid="stSidebar"]:not([aria-expanded="false"]) {
        min-width: 320px !important;
        max-width: 340px !important;
        width: 330px !important;
    }
    [data-testid="stSidebar"][aria-expanded="false"],
    .stApp:has([data-testid="stSidebarCollapsedControl"]) [data-testid="stSidebar"],
    .stApp:has([data-testid="collapsedControl"]) [data-testid="stSidebar"] {
        min-width: 0px !important;
        max-width: 0px !important;
        width: 0px !important;
        margin-left: 0px !important;
        margin-right: 0px !important;
        padding: 0px !important;
        border: none !important;
        overflow: hidden !important;
        display: none !important;
        transform: translateX(-100%) !important;
    }
    .sidebar-brand-title {
        font-size: 1.75rem;
        font-weight: 800;
        color: #60A5FA;
        margin-bottom: 0px;
        line-height: 1.15;
        letter-spacing: -0.01em;
    }
    .sidebar-brand-sub {
        font-size: 0.88rem;
        color: #9CA3AF;
        margin-bottom: 18px;
    }
    
    /* Model & Status Badges */
    .sidebar-section-title {
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #6B7280;
        margin-top: 16px;
        margin-bottom: 8px;
    }
    .model-info-card {
        background-color: #1F2937;
        border: 1px solid #374151;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 14px;
    }
    .model-name-title {
        font-weight: 700;
        font-size: 0.92rem;
        color: #38BDF8;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .model-detail-sub {
        font-size: 0.78rem;
        color: #9CA3AF;
        margin-top: 4px;
    }
    .status-pill-green {
        background-color: #064E3B;
        color: #34D399;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .privacy-pill {
        background-color: #1E1B4B;
        color: #A5B4FC;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 5px;
        border: 1px solid #312E81;
    }
    
    /* Knowledge Base Metric Boxes */
    .metric-card-box {
        background-color: #1F2937;
        border: 1px solid #374151;
        border-radius: 10px;
        padding: 14px;
        text-align: center;
    }
    .metric-card-num {
        font-size: 1.5rem;
        font-weight: 800;
        color: #F9FAFB;
    }
    .metric-card-label {
        font-size: 0.78rem;
        color: #9CA3AF;
        margin-top: 2px;
    }

    /* Main Header Area */
    .header-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-bottom: 24px;
        width: 100%;
        text-align: center;
    }
    .header-brand-row {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 16px;
    }
    .header-logo-box {
        background-color: #1F2937;
        border: 1px solid #374151;
        border-radius: 16px;
        padding: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        flex-shrink: 0;
    }
    .header-logo-img {
        width: 58px;
        height: 58px;
        border-radius: 12px;
        object-fit: cover;
        display: block;
    }
    .header-titles {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        text-align: left;
    }
    .header-icon-box {
        background-color: #1D4ED8;
        border-radius: 14px;
        padding: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    .main-title {
        font-size: 2.15rem;
        font-weight: 800;
        color: #F9FAFB;
        line-height: 1.15;
        margin-bottom: 3px;
        letter-spacing: -0.01em;
    }
    .main-subtitle {
        font-size: 1.02rem;
        font-weight: 600;
        color: #93C5FD;
        margin-bottom: 0px;
    }
    .main-desc {
        font-size: 0.92rem;
        color: #9CA3AF;
        text-align: center;
        margin-top: 14px;
        width: 100%;
        line-height: 1.4;
    }

    /* Source Reference Cards */
    .source-card {
        background-color: #1F2937;
        border-left: 4px solid #3B82F6;
        border-top: 1px solid #374151;
        border-right: 1px solid #374151;
        border-bottom: 1px solid #374151;
        padding: 12px 16px;
        margin-top: 8px;
        margin-bottom: 8px;
        border-radius: 8px;
    }
    .source-title {
        font-weight: 700;
        color: #60A5FA;
        font-size: 0.9rem;
    }
    .category-badge {
        background-color: #1E3A8A;
        color: #93C5FD;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .source-snippet {
        font-size: 0.85rem;
        color: #D1D5DB;
        font-style: italic;
        margin-top: 6px;
    }

    /* Unified Single-Row Search & Controls Dock Bar */
    .st-key-chat_unified_bar {
        position: fixed !important;
        bottom: 28px !important;
        z-index: 999 !important;
        background-color: rgba(15, 23, 42, 0.96) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid #334155 !important;
        border-radius: 16px !important;
        padding: 8px 12px !important;
        box-shadow: 0 12px 30px -5px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(255, 255, 255, 0.05) !important;
    }

    /* Desktop View: Centered in content area with safe max width */
    @media (min-width: 992px) {
        .st-key-chat_unified_bar {
            left: calc(50vw + 160px) !important;
            transform: translateX(-50%) !important;
            width: min(880px, calc(100vw - 370px)) !important;
        }
    }

    /* Mobile / Tablet / Collapsed Sidebar */
    @media (max-width: 991px) {
        .st-key-chat_unified_bar {
            left: 50% !important;
            transform: translateX(-50%) !important;
            width: calc(100vw - 32px) !important;
            max-width: 720px !important;
            padding: 6px 8px !important;
        }
    }

    /* Sidebar Collapsed State on Desktop */
    [data-testid="stSidebar"][aria-expanded="false"] ~ section[data-testid="stMain"] .st-key-chat_unified_bar,
    [data-testid="stSidebar"][aria-expanded="false"] ~ * .st-key-chat_unified_bar,
    [data-testid="stSidebarCollapsedControl"] ~ * .st-key-chat_unified_bar,
    [data-testid="collapsedControl"] + * .st-key-chat_unified_bar,
    .stApp:has([data-testid="stSidebar"][aria-expanded="false"]) .st-key-chat_unified_bar,
    .stApp:has([data-testid="stSidebarCollapsedControl"]) .st-key-chat_unified_bar {
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: min(880px, calc(100vw - 48px)) !important;
    }

    /* Zero out all Streamlit internal container gaps, widget margins, and column paddings */
    .st-key-chat_unified_bar [data-testid="stVerticalBlock"] {
        gap: 0px !important;
        padding: 0px !important;
        margin: 0px !important;
    }
    .st-key-chat_unified_bar [data-testid="stHorizontalBlock"] {
        align-items: center !important;
        gap: 8px !important;
        padding: 0px !important;
        margin: 0px !important;
    }
    .st-key-chat_unified_bar [data-testid="stColumn"] {
        padding: 0px !important;
        margin: 0px !important;
    }
    .st-key-chat_unified_bar [data-testid="stSelectbox"] {
        margin: 0px !important;
        padding: 0px !important;
    }
    .st-key-chat_unified_bar [data-testid="stChatInput"] {
        margin: 0px !important;
        padding: 0px !important;
        position: static !important;
        transform: none !important;
        width: 100% !important;
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        box-shadow: none !important;
    }
    .st-key-chat_unified_bar [data-testid="stChatInput"]:focus-within {
        border-color: #3B82F6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.25) !important;
    }
    .st-key-chat_unified_bar [data-testid="stButton"] {
        margin: 0px !important;
        padding: 0px !important;
    }
    .st-key-chat_unified_bar div[data-testid="stWidgetLabel"] {
        display: none !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Matching selectboxes inside unified dock bar */
    .st-key-chat_unified_bar [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        font-size: 0.84rem !important;
        font-weight: 500 !important;
        color: #F1F5F9 !important;
        height: 42px !important;
    }

    /* Clear chat button inside unified dock bar */
    .st-key-chat_unified_bar button {
        border-radius: 12px !important;
        border: 1px solid #334155 !important;
        background-color: #1E293B !important;
        color: #9CA3AF !important;
        height: 42px !important;
    }
    .st-key-chat_unified_bar button:hover {
        background-color: #374151 !important;
        color: #EF4444 !important;
        border-color: #EF4444 !important;
    }

    .chat-footer-hint {
        position: fixed !important;
        bottom: 8px !important;
        z-index: 998 !important;
        font-size: 0.74rem !important;
        color: #9CA3AF !important;
        text-align: center !important;
        pointer-events: none !important;
        user-select: none !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 5px !important;
    }
    @media (min-width: 992px) {
        .chat-footer-hint {
            left: calc(50vw + 160px) !important;
            transform: translateX(-50%) !important;
            width: min(880px, calc(100vw - 370px)) !important;
        }
    }
    @media (max-width: 991px) {
        .chat-footer-hint {
            left: 50% !important;
            transform: translateX(-50%) !important;
            width: calc(100vw - 32px) !important;
            max-width: 720px !important;
            bottom: 6px !important;
        }
    }
    /* Sidebar Collapsed State on Desktop - Footer Hint */
    [data-testid="stSidebar"][aria-expanded="false"] ~ section[data-testid="stMain"] .chat-footer-hint,
    [data-testid="stSidebar"][aria-expanded="false"] ~ * .chat-footer-hint,
    [data-testid="stSidebarCollapsedControl"] ~ * .chat-footer-hint,
    [data-testid="collapsedControl"] + * .chat-footer-hint,
    .stApp:has([data-testid="stSidebar"][aria-expanded="false"]) .chat-footer-hint,
    .stApp:has([data-testid="stSidebarCollapsedControl"]) .chat-footer-hint {
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: min(880px, calc(100vw - 48px)) !important;
    }

    .chat-bottom-spacer {
        height: 100px !important;
    }

    /* Executive Tab Navigation Styling */
    div[data-baseweb="tab-list"] {
        display: flex !important;
        justify-content: center !important;
        gap: 8px !important;
        border-bottom: 1px solid #1F2937 !important;
        background-color: transparent !important;
    }
    button[data-baseweb="tab"] {
        color: #9CA3AF !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        padding: 8px 18px !important;
        background-color: transparent !important;
        border: none !important;
    }
    button[data-baseweb="tab"]:hover {
        color: #F1F5F9 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #60A5FA !important;
    }
    div[data-baseweb="tab-highlight"] {
        background-color: #3B82F6 !important;
        height: 2px !important;
    }

    /* Professional Document Table Styling */
    .table-header-col {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #9CA3AF;
        padding-bottom: 6px;
    }
    .table-cell-text {
        font-size: 0.84rem;
        color: #E2E8F0;
        line-height: 1.4;
    }
    .category-pill {
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 600;
        display: inline-block;
        letter-spacing: 0.02em;
    }
    .cat-academic { background-color: #1E3A8A; color: #93C5FD; border: 1px solid #1D4ED8; }
    .cat-it { background-color: #083344; color: #67E8F9; border: 1px solid #0E7490; }
    .cat-projects { background-color: #3B0764; color: #D8B4FE; border: 1px solid #7E22CE; }
    .cat-policies { background-color: #451A03; color: #FCD34D; border: 1px solid #B45309; }
    .cat-notices { background-color: #431407; color: #FDBA74; border: 1px solid #C2410C; }
    .cat-guides { background-color: #064E3B; color: #6EE7B7; border: 1px solid #047857; }
    .cat-faqs { background-color: #172554; color: #93C5FD; border: 1px solid #2563EB; }
    .cat-research { background-color: #042F2E; color: #5EEAD4; border: 1px solid #0D9488; }
    .cat-other { background-color: #1E293B; color: #94A3B8; border: 1px solid #334155; }

    /* Delete Button Polish */
    .doc-row-del button {
        background-color: transparent !important;
        border: 1px solid #374151 !important;
        color: #9CA3AF !important;
        border-radius: 6px !important;
        padding: 2px 6px !important;
        transition: all 0.2s ease !important;
    }
    .doc-row-del button:hover {
        background-color: #7F1D1D !important;
        border-color: #EF4444 !important;
        color: #FEE2E2 !important;
    }

    /* Equal Height Guide Cards & Flex Column Stretching */
    div[data-testid="stTabContent"] [data-testid="stHorizontalBlock"] {
        align-items: stretch !important;
    }
    div[data-testid="stTabContent"] [data-testid="column"],
    div[data-testid="stTabContent"] [data-testid="stColumn"] {
        display: flex !important;
        flex-direction: column !important;
    }
    div[data-testid="stTabContent"] [data-testid="column"] > div,
    div[data-testid="stTabContent"] [data-testid="stColumn"] > div {
        flex: 1 1 auto !important;
        display: flex !important;
        flex-direction: column !important;
        height: 100% !important;
    }
    div[data-testid="stTabContent"] [data-testid="stMarkdownContainer"] {
        height: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        flex: 1 1 auto !important;
    }

    .guide-steps-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 16px;
        align-items: stretch;
        width: 100%;
        margin-bottom: 16px;
    }
    .guide-info-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 16px;
        align-items: stretch;
        width: 100%;
        margin-bottom: 16px;
    }
    @media (max-width: 768px) {
        .guide-steps-grid,
        .guide-info-grid {
            grid-template-columns: 1fr;
        }
    }

    .guide-step-card {
        background-color: #111827;
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 16px 18px;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        height: 100%;
        width: 100%;
    }
    .guide-info-card {
        background-color: #111827;
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 18px 20px;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        height: 100%;
        width: 100%;
    }
    </style>
"""


def apply_custom_styles():
    """Injects custom CSS styles into the active Streamlit app."""
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
