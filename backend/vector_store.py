import os
import io
import uuid
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
import pypdf

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class VectorStoreManager:
    """Manager for ChromaDB operations using fast local vector embeddings."""
    def __init__(self, db_dir: str = config.CHROMA_DB_DIR):
        self.db_dir = db_dir
        os.makedirs(self.db_dir, exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(path=self.db_dir)
        self.default_ef = DefaultEmbeddingFunction()

    def get_collection(self, provider: str = "gemini"):
        """Get or create ChromaDB collection using local ONNX embeddings (Zero API cost & 100% reliable)."""
        provider_lower = provider.lower().strip()
        collection_name = f"{config.COLLECTION_NAME}_{provider_lower}"
        
        return self.chroma_client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.default_ef,
            metadata={"hnsw:space": "cosine"}
        )

    def chunk_text(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """Split document text into overlapping chunks."""
        chunks = []
        if not text.strip():
            return chunks

        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start += chunk_size - chunk_overlap
            if start >= text_length:
                break
                
        return chunks

    def extract_text_from_file(self, file_bytes: bytes, filename: str) -> str:
        """Extract plain text from uploaded PDF, TXT, or MD files."""
        filename_lower = filename.lower()
        if filename_lower.endswith('.pdf'):
            pdf_reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            text = ""
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            return text
        else:
            return file_bytes.decode('utf-8', errors='ignore')

    def add_document(self, file_bytes: bytes, filename: str, provider: str = "gemini") -> int:
        """Process and store document chunks in ChromaDB."""
        text = self.extract_text_from_file(file_bytes, filename)
        if not text.strip():
            raise ValueError("Document contains no extractable text.")

        chunks = self.chunk_text(text)
        collection = self.get_collection(provider=provider)

        ids = [f"{filename}_{uuid.uuid4().hex[:8]}_{i}" for i in range(len(chunks))]
        metadatas = [{"source": filename, "chunk_index": i} for i in range(len(chunks))]

        collection.add(
            ids=ids,
            documents=chunks,
            metadatas=metadatas
        )

        return len(chunks)

    def search_similar(self, query: str, provider: str = "gemini", top_k: int = 4) -> List[Dict[str, Any]]:
        """Search ChromaDB for relevant text chunks matching the query."""
        collection = self.get_collection(provider=provider)
        
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )

        retrieved = []
        if results and 'documents' in results and results['documents']:
            docs = results['documents'][0]
            metas = results['metadatas'][0] if 'metadatas' in results and results['metadatas'] else [{}] * len(docs)
            distances = results['distances'][0] if 'distances' in results and results['distances'] else [0.0] * len(docs)
            
            for doc, meta, dist in zip(docs, metas, distances):
                retrieved.append({
                    "content": doc,
                    "metadata": meta,
                    "score": round(1 - dist, 4) if dist is not None else 1.0
                })

        return retrieved

    def list_documents(self, provider: str = "gemini") -> List[Dict[str, Any]]:
        """List summary of indexed documents in ChromaDB."""
        try:
            collection = self.get_collection(provider=provider)
            all_docs = collection.get(include=["metadatas"])
            metadatas = all_docs.get("metadatas", [])
            
            sources: Dict[str, int] = {}
            for meta in metadatas:
                if meta and "source" in meta:
                    src = meta["source"]
                    sources[src] = sources.get(src, 0) + 1
                    
            return [{"source": k, "chunk_count": v} for k, v in sources.items()]
        except Exception:
            return []

    def reset_db(self):
        """Reset all vector database collections."""
        try:
            cols = self.chroma_client.list_collections()
            for col in cols:
                self.chroma_client.delete_collection(col.name)
        except Exception:
            pass
