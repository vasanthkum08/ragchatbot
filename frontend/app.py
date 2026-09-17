import os
import uuid
import requests
import streamlit as st

# Configure page layout
st.set_page_config(
    page_title="AI Studio Chatbot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Professional Dark UI & Small Corner Badge
st.markdown("""
<style>
    /* Main Theme Overrides */
    .stApp {
        background-color: #0E1117;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header Container */
    .main-header {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        padding: 24px 32px;
        border-radius: 16px;
        border: 1px solid #334155;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    }
    .main-title {
        color: #F8FAFC;
        font-size: 28px;
        font-weight: 700;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .sub-title {
        color: #94A3B8;
        font-size: 14px;
        margin-top: 6px;
    }

    /* Small Corner Status Badge */
    .corner-badge-online {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: rgba(34, 197, 94, 0.12);
        color: #4ADE80;
        border: 1px solid rgba(74, 222, 128, 0.25);
        padding: 4px 10px;
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
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
    }

    /* Document Chip */
    .doc-chip {
        background: #1E293B;
        border: 1px solid #334155;
        color: #CBD5E1;
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 12px;
        margin-bottom: 6px;
        display: flex;
        justify-content: space-between;
    }

    /* Sidebar Clean Styling */
    section[data-testid="stSidebar"] {
        background-color: #0F172A;
        border-right: 1px solid #1E293B;
    }

    /* Chat Message Spacing */
    .stChatMessage {
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 12px;
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
    st.markdown("## ⚡ AI Workspace")
    
    # New Chat Button
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        save_current_session()
        st.session_state.session_id = str(uuid.uuid4())[:8]
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")

    # AI Provider Select
    provider_choice = st.radio(
        "AI Engine Provider:",
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
    with st.expander("📄 Document Indexing (RAG)", expanded=True):
        uploaded_file = st.file_uploader("Upload PDF, TXT, MD", type=["pdf", "txt", "md"])
        if uploaded_file is not None:
            if st.button("📤 Index File", use_container_width=True):
                with st.spinner("Indexing..."):
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                        data = {"provider": selected_provider}
                        resp = requests.post(f"{BACKEND_URL}/upload", files=files, data=data)
                        if resp.status_code == 200:
                            st.success("Indexed successfully!")
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
                    st.caption("Indexed Files:")
                    for d in docs:
                        st.markdown(f"<div class='doc-chip'>📄 {d['source']} <span>{d['chunk_count']} chunks</span></div>", unsafe_allow_html=True)
        except Exception:
            pass

    # Chat History List Accordion
    with st.expander("💬 Saved History", expanded=True):
        try:
            hist_resp = requests.get(f"{BACKEND_URL}/history/sessions", timeout=2)
            if hist_resp.status_code == 200:
                sessions = hist_resp.json().get("sessions", [])
                if not sessions:
                    st.caption("No previous chats saved yet.")
                for sess in sessions:
                    btn_label = f"💬 {sess['title']}"
                    if st.button(btn_label, key=f"sess_{sess['session_id']}", use_container_width=True):
                        msg_resp = requests.get(f"{BACKEND_URL}/history/session/{sess['session_id']}")
                        if msg_resp.status_code == 200:
                            st.session_state.session_id = sess['session_id']
                            st.session_state.messages = msg_resp.json().get("messages", [])
                            st.rerun()
        except Exception:
            st.caption("History offline.")

    st.markdown("---")

    # Controls Section: Clear Chat & Reset Database Buttons
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    with col_c2:
        if st.button("⚠️ Reset DB", use_container_width=True, help="Reset ChromaDB vector store collections"):
            try:
                res = requests.delete(f"{BACKEND_URL}/reset")
                if res.status_code == 200:
                    st.toast("✅ Vector Database Reset Successfully!")
                else:
                    st.error("Reset failed.")
            except Exception as e:
                st.error(f"Reset error: {e}")

    # Small Corner Status Badge (Tucked at bottom corner)
    st.markdown("<br>", unsafe_allow_html=True)
    if is_healthy:
        st.markdown("<div class='corner-badge-online'>● Server Online (127.0.0.1:8000)</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='corner-badge-offline'>● Server Offline</div>", unsafe_allow_html=True)


# --- MAIN CHAT UI ---

# Header Section
st.markdown("""
<div class="main-header">
    <div class="main-title">
        ⚡ Enterprise AI Assistant & RAG Studio
    </div>
    <div class="sub-title">
        Ask general questions OR upload documents for grounded intelligence • Powered by Gemini & OpenAI
    </div>
</div>
""", unsafe_allow_html=True)

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sources" in msg and msg["sources"]:
            with st.expander("📚 Context Sources"):
                for idx, src in enumerate(msg["sources"], 1):
                    st.markdown(f"**Source {idx}:** `{src.get('metadata', {}).get('source', 'Unknown')}`")
                    st.text(src.get('content', '')[:300] + "...")

# Chat Input Box
if prompt := st.chat_input("Ask anything or inquire about your uploaded documents..."):
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
            with st.spinner("Generating answer..."):
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
                            with st.expander("📚 Context Sources"):
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
                    else:
                        err_msg = resp.json().get('detail', resp.text)
                        st.error(f"API Error: {err_msg}")
                except Exception as e:
                    st.error(f"Backend connection error: {e}")
