# RAG Chatbot - Streamlit + FastAPI + ChromaDB + OpenAI API

A complete Retrieval-Augmented Generation (RAG) chatbot system matching the architecture diagram, integrated with **OpenAI API** (LLM and Embeddings).

## Architecture Components

- **Frontend UI**: Streamlit (`frontend/app.py`)
- **Backend API**: FastAPI Server (`backend/main.py`)
- **Vector DB**: ChromaDB (`data/chroma_db/`)
- **LLM & Embeddings**: OpenAI API (`text-embedding-3-small` and `gpt-4o-mini`)

---

## Quick Setup Guide

### 1. Install Dependencies
Run the following command in your terminal:
```bash
pip install -r requirements.txt
```

### 2. Configure OpenAI API Key
Either edit `.env` and set your key:
```env
OPENAI_API_KEY=sk-...
```
OR enter your OpenAI API key directly in the Streamlit Sidebar UI after starting the app!

---

## Running the Application

### Step 1: Start FastAPI Backend
```bash
python run_backend.py
```
FastAPI server will be running at `http://127.0.0.1:8000` (API Docs at `http://127.0.0.1:8000/docs`).

### Step 2: Start Streamlit Frontend UI
In a separate terminal window:
```bash
python run_frontend.py
```
Streamlit will open in your web browser at `http://localhost:8501`.

---

## Features

1. **Document Upload & Indexing**: Upload `.pdf`, `.txt`, or `.md` files via the UI. Texts are chunked and converted to embeddings using OpenAI and saved to ChromaDB.
2. **Interactive RAG Chat**: Ask questions in the chat interface. High-relevance context is retrieved from ChromaDB and sent to OpenAI `gpt-4o-mini` to generate grounded answers.
3. **Source Citation**: Expand the "Retrieved Source Documents" section under any message to verify the context chunks used to answer your query.
