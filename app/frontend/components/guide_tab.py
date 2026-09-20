"""Guide tab component ("How to Use?") for ContextIQ Streamlit frontend."""

import streamlit as st


def render_guide_tab():
    """Renders the comprehensive 'How to Use?' user manual, controls reference, and privacy guide."""
    st.markdown("""
    <div style="font-size: 1.25rem; font-weight: 700; color: #F9FAFB; margin-bottom: 3px;">Getting Started & User Guide</div>
    <div style="font-size: 0.88rem; color: #9CA3AF; margin-bottom: 18px;">A comprehensive walkthrough for configuring, querying, and managing your ContextIQ knowledge base.</div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="guide-steps-grid">
        <div class="guide-step-card">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                <span style="background-color: #1E3A8A; color: #93C5FD; font-size: 0.76rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; letter-spacing: 0.04em;">STEP 1</span>
                <span style="font-size: 0.95rem; font-weight: 600; color: #F1F5F9;">Configure API Key</span>
            </div>
            <div style="font-size: 0.84rem; color: #9CA3AF; line-height: 1.6; flex: 1;">
                Open the left sidebar and enter your <b>Groq</b> or <b>OpenAI</b> API key. Keys persist securely in your browser session. Free Groq keys are available at <a href="https://console.groq.com/keys" target="_blank" style="color: #60A5FA; text-decoration: none;">console.groq.com</a>.
            </div>
        </div>
        <div class="guide-step-card">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                <span style="background-color: #1E3A8A; color: #93C5FD; font-size: 0.76rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; letter-spacing: 0.04em;">STEP 2</span>
                <span style="font-size: 0.95rem; font-weight: 600; color: #F1F5F9;">Upload Documents</span>
            </div>
            <div style="font-size: 0.84rem; color: #9CA3AF; line-height: 1.6; flex: 1;">
                Navigate to the <b>Document Management</b> tab. Drag and drop PDF files (resumes, job descriptions, manuals, research), choose a category tag, and click <b>Process & Index Documents</b>.
            </div>
        </div>
        <div class="guide-step-card">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                <span style="background-color: #1E3A8A; color: #93C5FD; font-size: 0.76rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; letter-spacing: 0.04em;">STEP 3</span>
                <span style="font-size: 0.95rem; font-weight: 600; color: #F1F5F9;">Ask the Assistant</span>
            </div>
            <div style="font-size: 0.84rem; color: #9CA3AF; line-height: 1.6; flex: 1;">
                Switch to <b>Ask Assistant</b>. Ask natural language questions in the bottom console bar. ContextIQ retrieves relevant chunks and generates grounded answers with exact source citations.
            </div>
        </div>
    </div>

    <div class="guide-info-grid">
        <div class="guide-info-card">
            <div style="font-size: 0.96rem; font-weight: 600; color: #F1F5F9; margin-bottom: 10px;">Search Bar Controls & Settings</div>
            <div style="font-size: 0.85rem; color: #9CA3AF; line-height: 1.65; flex: 1;">
                <b style="color: #60A5FA;">Category Selector (Left):</b><br>
                Restricts retrieval to a specific document category (e.g. <i>Academic</i>, <i>Policies</i>, <i>IT</i>). To compare across multiple documents (e.g., comparing your resume with a job description), select <b>All Categories</b> to enable automatic multi-document retrieval.<br><br>
                <b style="color: #60A5FA;">Top Chunks (Right):</b><br>
                Controls how many text excerpts (chunks) are extracted from your documents to ground the answer. Each chunk contains a relevant passage with exact page citations. Choose <b>Top 2–4 Chunks</b> for focused Q&A, or <b>Top 6–10 Chunks</b> for comprehensive multi-document comparisons.<br><br>
                <b style="color: #60A5FA;">Clear Chat Button (🗑):</b><br>
                Clears conversation history to start a new inquiry with a clean slate.
            </div>
        </div>
        <div class="guide-info-card">
            <div style="font-size: 0.96rem; font-weight: 600; color: #F1F5F9; margin-bottom: 10px;">Recommended Query Patterns & Privacy</div>
            <div style="font-size: 0.85rem; color: #9CA3AF; line-height: 1.65; flex: 1;">
                <b style="color: #D1D5DB;">Resume & Alignment Inquiries:</b><br>
                • "Summarize my resume and professional background"<br>
                • "Is the shared job description aligns with my resume?"<br><br>
                <b style="color: #D1D5DB;">Comparative & Cross-Document Analysis:</b><br>
                • "What are the key differences between the two policies?"<br>
                • "Does the candidate have the qualifications needed for this role?"<br><br>
                <b style="color: #D1D5DB;">Privacy & On-Premise Embeddings:</b><br>
                • Your workspace is 100% private to your session ID.<br>
                • Vector embeddings run locally on your machine via HuggingFace (no document data sent to external embedding APIs).
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
