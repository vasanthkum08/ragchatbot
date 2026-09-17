import os
import uuid
import requests
import streamlit as st

# Configure page layout
st.set_page_config(
    page_title="RAG Chatbot AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Fixed Bottom Dock Positioning & Clean Typography
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* Overall Background */
    .stApp {
        background: radial-gradient(circle at 50% -20%, #1E1B4B 0%, #0B0D17 50%, #05060A 100%) !important;
        color: #F8FAFC !important;
    }

    /* Main Container Padding to Prevent Fixed Bottom Dock Overlap */
    .main .block-container {
        padding-bottom: 160px !important;
    }

    /* Top Navigation Header Banner */
    .app-header {
        background: rgba(15, 23, 42, 0.75) !important;
        backdrop-filter: blur(24px) saturate(200%) !important;
        -webkit-backdrop-filter: blur(24px) saturate(200%) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 18px 24px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4) !important;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .brand-title {
        font-size: 22px !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #FFFFFF 0%, #CBD5E1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .brand-subtitle {
        color: #94A3B8;
        font-size: 13px;
        margin-top: 2px;
        font-weight: 500;
    }

    .tech-pill {
        background: rgba(99, 102, 241, 0.12);
        border: 1px solid rgba(99, 102, 241, 0.3);
        color: #818CF8;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
    }

    /* Hero Suggestion Cards (Empty State) */
    .hero-container {
        text-align: center;
        padding: 30px 20px 20px 20px;
    }
    .hero-heading {
        font-size: 28px;
        font-weight: 800;
        background: linear-gradient(135deg, #818CF8 0%, #C084FC 50%, #60A5FA 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }
    .hero-sub {
        color: #94A3B8;
        font-size: 14px;
        margin-bottom: 24px;
    }

    /* Prompt Suggestion Button Styling */
    div.stButton > button[type="secondary"] {
        background: rgba(30, 41, 59, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 14px !important;
        padding: 14px 18px !important;
        color: #E2E8F0 !important;
        text-align: left !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    }

    div.stButton > button[type="secondary"]:hover {
        background: rgba(49, 46, 129, 0.4) !important;
        border-color: rgba(99, 102, 241, 0.4) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.25) !important;
        color: #FFFFFF !important;
    }

    /* Chat Messages - Sleek Modern Cards */
    div[data-testid="stChatMessage"] {
        background: rgba(15, 23, 42, 0.6) !important;
        backdrop-filter: blur(16px) !important;
        border-radius: 16px !important;
        padding: 16px 20px !important;
        margin-bottom: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2) !important;
    }

    /* User Message Glass Pill */
    div[data-testid="stChatMessage"]:nth-child(even) {
        background: rgba(30, 27, 75, 0.45) !important;
        border: 1px solid rgba(99, 102, 241, 0.25) !important;
        box-shadow: 0 8px 20px rgba(79, 70, 229, 0.15) !important;
    }

    /* Original Clean Text Box Style FIXED AT BOTTOM */
    div[data-testid="stChatInput"] {
        border-radius: 16px !important;
        border: 1.5px solid #334155 !important;
        background: #1E293B !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35) !important;
        transition: all 0.25s ease !important;
        padding: 4px 8px !important;
    }
    
    div[data-testid="stChatInput"]:focus-within {
        border-color: #3B82F6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.25), 0 8px 32px rgba(0, 0, 0, 0.45) !important;
        background: #0F172A !important;
    }

    div[data-testid="stChatInput"] textarea {
        color: #F8FAFC !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        line-height: 1.5 !important;
        background: transparent !important;
    }

    div[data-testid="stChatInput"] textarea::placeholder {
        color: #64748B !important;
        font-size: 14px !important;
    }

    /* Original Blue Send Button */
    div[data-testid="stChatInput"] button {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        border: none !important;
        border-radius: 10px !important;
        color: #FFFFFF !important;
        transition: transform 0.15s ease, background 0.2s ease !important;
    }

    div[data-testid="stChatInput"] button:hover {
        transform: scale(1.05) !important;
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%) !important;
        box-shadow: 0 2px 12px rgba(59, 130, 246, 0.45) !important;
    }

    /* Sidebar Clean Translucent Dark Styling */
    section[data-testid="stSidebar"] {
        background-color: #07090E !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
    }

    /* Primary Accent Button */
    div.stButton > button[type="primary"] {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
        border-radius: 12px !important;
        border: none !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 16px rgba(124, 58, 237, 0.35) !important;
        transition: all 0.2s ease !important;
    }

    /* Document Chip */
    .doc-chip {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        color: #CBD5E1;
        padding: 6px 10px;
        border-radius: 8px;
        font-size: 12px;
        margin-bottom: 6px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Corner Status Badge */
    .corner-badge-online {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: rgba(34, 197, 94, 0.12);
        color: #4ADE80;
        border: 1px solid rgba(74, 222, 128, 0.25);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
    }
    .corner-badge-offline {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: rgba(239, 68, 68, 0.12);
        color: #F87171;
        border: 1px solid rgba(248, 113, 113, 0.25);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Backend URL configuration
FASTAPI_HOST = os.getenv("FASTAPI_HOST", "127.0.0.1")
FASTAPI_PORT = os.getenv("FASTAPI_PORT", "8000")
BACKEND_URL = f"http://{FASTAPI_HOST}:{FASTAPI_PORT}"

# Initialize session state variables
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

if "messages" not in st.session_state:
    st.session_state.messages = []

if "provider" not in st.session_state:
    st.session_state.provider = "gemini"

if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = os.getenv("GEMINI_API_KEY", "AIzaSyC8MPpgmstJyrc7TdQTohPG2WkQpgbgWWA")

if "openai_api_key" not in st.session_state:
    st.session_state.openai_api_key = os.getenv("OPENAI_API_KEY", "")

if "suggested_prompt" not in st.session_state:
    st.session_state.suggested_prompt = ""


def check_backend_health():
    """Check if FastAPI backend server is accessible."""
    try:
        resp = requests.get(f"{BACKEND_URL}/health", timeout=2)
        return resp.status_code == 200, resp.json() if resp.status_code == 200 else None
    except Exception:
        return False, None


def save_current_session():
    """Save current chat session to backend persistent history."""
    if st.session_state.messages:
        first_user_msg = next((m["content"] for m in st.session_state.messages if m["role"] == "user"), "Chat Conversation")
        title = first_user_msg[:35]
        try:
            from backend.history_manager import HistoryManager
            HistoryManager.save_session(st.session_state.session_id, title, st.session_state.messages)
        except Exception:
            pass


# Check Server Status
is_healthy, _ = check_backend_health()

# --- SIDEBAR UI ---
with st.sidebar:
    st.markdown("## ⚡ RAG Chatbot AI")
    
    # New Chat Button
    if st.button("➕ New Chat Session", use_container_width=True, type="primary"):
        save_current_session()
        st.session_state.session_id = str(uuid.uuid4())[:8]
        st.session_state.messages = []
        st.session_state.suggested_prompt = ""
        st.rerun()

    st.markdown("---")

    # AI Provider Select
    provider_choice = st.radio(
        "Select AI Model Engine:",
        options=["Google Gemini (FREE)", "OpenAI"],
        index=0 if st.session_state.provider == "gemini" else 1
    )
    selected_provider = "gemini" if "Gemini" in provider_choice else "openai"
    st.session_state.provider = selected_provider

    # API Key Input
    if selected_provider == "gemini":
        api_key_input = st.text_input(
            "Gemini API Key:",
            value=st.session_state.gemini_api_key,
            type="password",
            placeholder="AIzaSy..."
        )
        st.session_state.gemini_api_key = api_key_input.strip()
        active_api_key = st.session_state.gemini_api_key
    else:
        api_key_input = st.text_input(
            "OpenAI API Key:",
            value=st.session_state.openai_api_key,
            type="password",
            placeholder="sk-..."
        )
        st.session_state.openai_api_key = api_key_input.strip()
        active_api_key = st.session_state.openai_api_key

    st.markdown("---")

    # Document Indexing Accordion
    with st.expander("📁 Document Knowledge Base (RAG)", expanded=True):
        sidebar_file = st.file_uploader("Upload PDF, TXT, MD, PNG, JPG", type=["pdf", "txt", "md", "png", "jpg", "jpeg"], key="sidebar_file_uploader")
        if sidebar_file is not None:
            if st.button("📥 Upload & Index Document", use_container_width=True):
                with st.spinner("Indexing vector embeddings..."):
                    try:
                        files = {"file": (sidebar_file.name, sidebar_file.getvalue())}
                        data = {"provider": selected_provider}
                        resp = requests.post(f"{BACKEND_URL}/upload", files=files, data=data)
                        if resp.status_code == 200:
                            st.toast("✅ File Indexed Successfully!")
                        else:
                            st.error(resp.json().get("detail", "Upload failed"))
                    except Exception as e:
                        st.error(f"Error: {e}")

        # List Indexed Documents
        try:
            doc_resp = requests.get(f"{BACKEND_URL}/documents?provider={selected_provider}", timeout=2)
            if doc_resp.status_code == 200:
                docs = doc_resp.json().get("documents", [])
                if docs:
                    st.caption("Indexed Knowledge Base:")
                    for d in docs:
                        st.markdown(f"<div class='doc-chip'>📄 <b>{d['source']}</b> <span>{d['chunk_count']} chunks</span></div>", unsafe_allow_html=True)
        except Exception:
            pass

    # Saved Chat History List Accordion with Individual Delete Button
    with st.expander("💬 History & Threads", expanded=True):
        try:
            hist_resp = requests.get(f"{BACKEND_URL}/history/sessions", timeout=2)
            if hist_resp.status_code == 200:
                sessions = hist_resp.json().get("sessions", [])
                if not sessions:
                    st.caption("No previous sessions recorded.")
                for sess in sessions:
                    col_s1, col_s2 = st.columns([0.8, 0.2])
                    with col_s1:
                        btn_label = f"💬 {sess['title']}"
                        if st.button(btn_label, key=f"sess_{sess['session_id']}", use_container_width=True):
                            msg_resp = requests.get(f"{BACKEND_URL}/history/session/{sess['session_id']}")
                            if msg_resp.status_code == 200:
                                st.session_state.session_id = sess['session_id']
                                st.session_state.messages = msg_resp.json().get("messages", [])
                                st.session_state.suggested_prompt = ""
                                st.rerun()
                    with col_s2:
                        if st.button("🗑️", key=f"del_{sess['session_id']}", help="Delete chat history thread"):
                            requests.delete(f"{BACKEND_URL}/history/session/{sess['session_id']}")
                            if st.session_state.session_id == sess['session_id']:
                                st.session_state.messages = []
                            st.toast("Chat history thread deleted!")
                            st.rerun()
        except Exception:
            st.caption("History service offline.")

    st.markdown("---")

    # Controls Section: Clear Chat & Reset Database Buttons
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        if st.button("🗑️ Clear Current", use_container_width=True):
            st.session_state.messages = []
            st.session_state.suggested_prompt = ""
            st.rerun()

    with col_c2:
        if st.button("⚠️ Reset DB", use_container_width=True, help="Reset ChromaDB vector store collections"):
            try:
                res = requests.delete(f"{BACKEND_URL}/reset")
                if res.status_code == 200:
                    st.toast("✅ Vector DB Reset Successfully!")
                else:
                    st.error("Reset failed.")
            except Exception as e:
                st.error(f"Reset error: {e}")

    # Small Corner Status Badge
    st.markdown("<br>", unsafe_allow_html=True)
    if is_healthy:
        st.markdown("<div class='corner-badge-online'>● Server Online (127.0.0.1:8000)</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='corner-badge-offline'>● Server Offline</div>", unsafe_allow_html=True)


# --- MAIN INTERFACE ---

# Header Banner
st.markdown(f"""
<div class="app-header">
    <div>
        <div class="brand-title">
            ⚡ RAG Chatbot AI
        </div>
        <div class="brand-subtitle">
            FastAPI + Streamlit + ChromaDB + Gemini / OpenAI API
        </div>
    </div>
    <div>
        <span class="tech-pill">Engine: {selected_provider.upper()}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# HERO SUGGESTION DASHBOARD (When no messages yet)
if not st.session_state.messages:
    st.markdown("""
    <div class="hero-container">
        <div class="hero-heading">What would you like to explore today?</div>
        <div class="hero-sub">Ask any question or upload documents to get grounded AI answers</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 **Analyze Document Insights**\n\nSummarize key findings or extract data from uploaded files", use_container_width=True, type="secondary"):
            st.session_state.suggested_prompt = "Summarize the key insights and main points from the uploaded document."
            st.rerun()

        if st.button("💡 **Creative Problem Solving**\n\nBrainstorm innovative concepts, strategies, and solutions", use_container_width=True, type="secondary"):
            st.session_state.suggested_prompt = "Give me 5 innovative ideas to improve project productivity and AI automation."
            st.rerun()

    with col2:
        if st.button("💻 **Code & Technical Architecture**\n\nHelp design, debug, or explain complex software logic", use_container_width=True, type="secondary"):
            st.session_state.suggested_prompt = "Explain how FastAPI, Streamlit, and ChromaDB work together in a modern RAG system."
            st.rerun()

        if st.button("🔍 **Deep Domain Q&A**\n\nAsk multi-step questions and receive comprehensive answers", use_container_width=True, type="secondary"):
            st.session_state.suggested_prompt = "What are the best practices for building scalable RAG applications with vector databases?"
            st.rerun()

# Display Chat Messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sources" in msg and msg["sources"]:
            with st.expander("📚 Retrieved Knowledge Sources"):
                for idx, src in enumerate(msg["sources"], 1):
                    st.markdown(f"**Source {idx}:** `{src.get('metadata', {}).get('source', 'Unknown')}`")
                    st.text(src.get('content', '')[:300] + "...")

# Top-level st.chat_input ALWAYS stays fixed at the screen bottom in Streamlit's native bottom dock!
prompt_input_val = st.chat_input("Ask anything or inquire about your uploaded documents...")
prompt = prompt_input_val or st.session_state.suggested_prompt

if prompt:
    # Reset suggested prompt trigger
    st.session_state.suggested_prompt = ""

    if not active_api_key:
        st.error(f"Please enter your {selected_provider.upper()} API Key in the left sidebar.")
    elif not is_healthy:
        st.error("Backend server is offline. Please start the backend with `python run_backend.py`.")
    else:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Send request to FastAPI backend
        with st.chat_message("assistant"):
            with st.spinner("Generating intelligent response..."):
                try:
                    payload = {
                        "query": prompt,
                        "provider": selected_provider,
                        "top_k": 4,
                        "api_key": active_api_key,
                        "session_id": st.session_state.session_id,
                        "chat_history": st.session_state.messages[:-1]
                    }
                    resp = requests.post(f"{BACKEND_URL}/query", json=payload, timeout=60)
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        answer = data.get("answer", "No response generated.")
                        sources = data.get("sources", [])

                        st.markdown(answer)
                        if sources:
                            with st.expander("📚 Retrieved Knowledge Sources"):
                                for idx, src in enumerate(sources, 1):
                                    st.markdown(f"**Source {idx}:** `{src.get('metadata', {}).get('source', 'Unknown')}`")
                                    st.text(src.get('content', '')[:300] + "...")

                        # Update session history
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "sources": sources
                        })
                        save_current_session()
                        st.rerun()
                    else:
                        err_msg = resp.json().get('detail', resp.text)
                        st.error(f"API Error: {err_msg}")
                except Exception as e:
                    st.error(f"Backend connection error: {e}")
