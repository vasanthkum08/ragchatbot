import os
import json
import uuid
from typing import List, Dict, Any

HISTORY_DIR = "./data/chat_history"
os.makedirs(HISTORY_DIR, exist_ok=True)


class HistoryManager:
    """Manages persistent chat conversation history in JSON files."""

    @staticmethod
    def get_all_sessions() -> List[Dict[str, Any]]:
        """List all saved chat sessions."""
        sessions = []
        if not os.path.exists(HISTORY_DIR):
            return sessions

        for filename in sorted(os.listdir(HISTORY_DIR), reverse=True):
            if filename.endswith(".json"):
                filepath = os.path.join(HISTORY_DIR, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        sessions.append({
                            "session_id": data.get("session_id", filename[:-5]),
                            "title": data.get("title", "Chat Conversation"),
                            "created_at": data.get("created_at", ""),
                            "message_count": len(data.get("messages", []))
                        })
                except Exception:
                    continue
        return sessions

    @staticmethod
    def load_session(session_id: str) -> List[Dict[str, Any]]:
        """Load messages from a specific session ID."""
        filepath = os.path.join(HISTORY_DIR, f"{session_id}.json")
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("messages", [])
            except Exception:
                pass
        return []

    @staticmethod
    def save_session(session_id: str, title: str, messages: List[Dict[str, Any]]):
        """Save session messages to disk."""
        filepath = os.path.join(HISTORY_DIR, f"{session_id}.json")
        data = {
            "session_id": session_id,
            "title": title[:40] if title else "Chat Conversation",
            "messages": messages
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def delete_session(session_id: str):
        """Delete a chat session."""
        filepath = os.path.join(HISTORY_DIR, f"{session_id}.json")
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception:
                pass
