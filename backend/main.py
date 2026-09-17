import os
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from backend.vector_store import VectorStoreManager
from backend.rag_chain import RAGChain
from backend.history_manager import HistoryManager

app = FastAPI(
    title="RAG Chatbot API Server",
    description="FastAPI Backend for Professional RAG & General AI Chatbot.",
    version="1.3.0"
)

# Enable CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vector_manager = VectorStoreManager()


class QueryRequest(BaseModel):
    query: str
    provider: Optional[str] = "gemini"
    top_k: Optional[int] = 4
    api_key: Optional[str] = None
    session_id: Optional[str] = None
    chat_history: Optional[List[Dict[str, Any]]] = None


class QueryResponse(BaseModel):
    query: str
    answer: str
    provider: str
    sources: List[Dict[str, Any]]


def resolve_api_key(provider: str, request_api_key: Optional[str] = None, header_api_key: Optional[str] = Header(None, alias="X-Api-Key")) -> str:
    """Resolve API key priority for the chosen LLM provider."""
    provider_lower = provider.lower().strip()
    env_key = config.OPENAI_API_KEY if provider_lower == "openai" else config.GEMINI_API_KEY
    
    key = request_api_key or header_api_key or env_key
    if not key or not key.strip():
        raise HTTPException(
            status_code=400,
            detail=f"{provider.upper()} API Key is missing. Please enter your {provider.upper()} API Key in the UI sidebar."
        )
    return key.strip()


@app.get("/")
def read_root():
    return {"status": "online", "message": "Professional RAG & AI Backend API Server running!"}


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "vector_db": os.path.exists(config.CHROMA_DB_DIR),
        "embedding_engine": "Local ONNX MiniLM (100% Free & Fast)",
        "default_provider": config.DEFAULT_PROVIDER,
        "gemini_llm": config.GEMINI_LLM_MODEL,
        "openai_llm": config.OPENAI_LLM_MODEL
    }


@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    provider: Optional[str] = Form("gemini")
):
    """Upload and index a document (PDF, TXT, MD) into ChromaDB using local embeddings."""
    resolved_provider = provider or "gemini"
    
    filename = file.filename
    contents = await file.read()
    
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        chunks_count = vector_manager.add_document(
            file_bytes=contents,
            filename=filename,
            provider=resolved_provider
        )
        return {
            "status": "success",
            "filename": filename,
            "provider": resolved_provider,
            "chunks_indexed": chunks_count,
            "message": f"Successfully indexed {filename} ({chunks_count} chunks)."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to index document: {str(e)}")


@app.post("/query", response_model=QueryResponse)
def query_rag(payload: QueryRequest):
    """Query ChromaDB (or general AI if no docs) and generate grounded/general response."""
    resolved_provider = payload.provider or "gemini"
    resolved_key = resolve_api_key(provider=resolved_provider, request_api_key=payload.api_key)

    if not payload.query or not payload.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")

    try:
        # Step 1: Search ChromaDB using local fast embeddings
        retrieved_chunks = vector_manager.search_similar(
            query=payload.query,
            provider=resolved_provider,
            top_k=payload.top_k or 4
        )

        # Step 2: Generate response using LLM (Gemini or OpenAI) with fallback to general knowledge
        answer = RAGChain.generate_response(
            api_key=resolved_key,
            query=payload.query,
            context_chunks=retrieved_chunks,
            provider=resolved_provider,
            chat_history=payload.chat_history
        )

        return QueryResponse(
            query=payload.query,
            answer=answer,
            provider=resolved_provider,
            sources=retrieved_chunks if retrieved_chunks else []
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")


@app.get("/documents")
def get_documents(provider: Optional[str] = "gemini"):
    """List indexed document sources and their chunk count."""
    try:
        resolved_provider = provider or "gemini"
        documents = vector_manager.list_documents(provider=resolved_provider)
        return {"documents": documents}
    except Exception as e:
        return {"documents": [], "error": str(e)}


@app.delete("/reset")
def reset_database():
    """Reset the vector database collections."""
    try:
        vector_manager.reset_db()
        return {"status": "success", "message": "Vector database reset successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")


# History Endpoints
@app.get("/history/sessions")
def get_history_sessions():
    return {"sessions": HistoryManager.get_all_sessions()}


@app.get("/history/session/{session_id}")
def get_session_messages(session_id: str):
    return {"messages": HistoryManager.load_session(session_id)}


@app.delete("/history/session/{session_id}")
def delete_session(session_id: str):
    HistoryManager.delete_session(session_id)
    return {"status": "success"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=config.FASTAPI_HOST, port=config.FASTAPI_PORT, reload=True)
