import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyC8MPpgmstJyrc7TdQTohPG2WkQpgbgWWA")

# Default AI Provider ("gemini" or "openai")
DEFAULT_PROVIDER = os.getenv("AI_PROVIDER", "gemini")

# FastAPI Settings
FASTAPI_HOST = os.getenv("FASTAPI_HOST", "127.0.0.1")
FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", "8000"))
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./data/chroma_db")

# Model configurations
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
OPENAI_LLM_MODEL = "gpt-4o-mini"

GEMINI_LLM_MODEL = "gemini-3.5-flash-lite"
GEMINI_FALLBACK_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-1.5-flash-latest",
    "gemini-flash-latest",
    "gemini-2.5-flash-lite"
]

COLLECTION_NAME = "rag_documents"
