import re
from langchain_core.prompts import ChatPromptTemplate

GREETING_PATTERNS = [
    r"^(hi|hello|hey|heya|hullo|greetings|hola|howdy)(\s+.*)?$",
    r"^good\s+(morning|afternoon|evening|day)(\s+.*)?$",
    r"^how\s+are\s+you(\s+today)?\??$",
    r"^who\s+are\s+you\??$",
    r"^what\s+(can\s+you\s+do|is\s+this|are\s+you)\??$",
    r"^(thanks|thank\s+you|thx)(\s+.*)?$",
    r"^help(\s+me)?\??$"
]

GREETING_RESPONSES = {
    "greeting": (
        "Hello! I am **ContextIQ**, your personal context-aware knowledge assistant.\n\n"
        "I can help you analyze, search, and answer questions about your uploaded PDF documents. "
        "Upload your files in the **Documents** tab or ask me a question about any document you've already indexed!"
    ),
    "thanks": (
        "You're welcome! Let me know if you have any more questions about your uploaded documents."
    )
}


def is_greeting_query(query: str) -> bool:
    """
    Determines if a user input is a general conversational greeting or salutation.
    """
    cleaned = query.strip().lower()
    # Check short 1-2 word inputs
    if len(cleaned.split()) <= 3:
        for pattern in GREETING_PATTERNS:
            if re.match(pattern, cleaned):
                return True
    return False


def get_greeting_response(query: str) -> str:
    """
    Returns an appropriate friendly response for general greetings.
    """
    cleaned = query.strip().lower()
    if any(kw in cleaned for kw in ["thank", "thanks", "thx"]):
        return GREETING_RESPONSES["thanks"]
    return GREETING_RESPONSES["greeting"]


RAG_SYSTEM_PROMPT = """You are ContextIQ, a helpful and precise document intelligence assistant.

Your primary goal is to answer the user's question using ONLY the provided document context chunks.

STRICT GROUNDING & FORMATTING RULES:
1. Base your answer STRICTLY on the facts contained in the Context below.
2. Do NOT invent, assume, or extrapolate facts not present in the Context.
3. If the provided Context does NOT contain sufficient information to answer the question, respond EXACTLY:
   "I couldn't find sufficient information about this in your uploaded documents."
4. Format your output cleanly in natural markdown text. Do NOT include raw bracket citation codes like 【3†L1-L4】 or [1†source] in your response.

Context:
{context}
"""

RAG_USER_PROMPT = """Question: {question}"""


def get_rag_prompt_template() -> ChatPromptTemplate:
    """
    Returns the ChatPromptTemplate for ContextIQ RAG generation.
    """
    return ChatPromptTemplate.from_messages([
        ("system", RAG_SYSTEM_PROMPT),
        ("human", RAG_USER_PROMPT)
    ])


INSUFFICIENT_CONTEXT_RESPONSE = "I couldn't find sufficient information about this in your uploaded documents."
