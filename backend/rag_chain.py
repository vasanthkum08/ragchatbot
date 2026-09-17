import os
from typing import List, Dict, Any
from openai import OpenAI
from google import genai

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class RAGChain:
    """RAG chain handler supporting both document-grounded answers and general conversational AI."""

    @staticmethod
    def generate_response(
        api_key: str,
        query: str,
        context_chunks: List[Dict[str, Any]],
        provider: str = "gemini",
        chat_history: List[Dict[str, str]] = None
    ) -> str:
        """Generate a response using context if available, or general knowledge if no documents are uploaded."""
        if not api_key:
            raise ValueError(f"{provider.upper()} API key is missing.")

        provider_lower = provider.lower().strip()
        history_text = ""
        if chat_history:
            recent_turns = chat_history[-6:]  # Keep last 3 turns for context
            history_lines = [f"{msg['role'].capitalize()}: {msg['content']}" for msg in recent_turns]
            history_text = "Conversation History:\n" + "\n".join(history_lines) + "\n\n"

        if context_chunks:
            context_parts = []
            for i, chunk in enumerate(context_chunks, 1):
                source = chunk.get("metadata", {}).get("source", "Unknown")
                content = chunk.get("content", "")
                context_parts.append(f"--- Document Source [{i}]: {source} ---\n{content}")
            context_text = "\n\n".join(context_parts)

            system_instruction = (
                "You are an expert AI Assistant. Answer the user's question primarily using the provided document context. "
                "If the context provides useful details, synthesize them clearly. You may supplement with general knowledge if needed to make the answer comprehensive and clear."
            )
            prompt_content = f"{history_text}Context Information:\n{context_text}\n\nUser Question: {query}\n\nAnswer:"
        else:
            system_instruction = (
                "You are an expert AI Assistant. Answer the user's question accurately, helpfully, and professionally using your general knowledge."
            )
            prompt_content = f"{history_text}User Question: {query}\n\nAnswer:"

        if provider_lower == "openai":
            client = OpenAI(api_key=api_key)
            messages = [{"role": "system", "content": system_instruction}]
            if chat_history:
                for msg in chat_history[-6:]:
                    messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": prompt_content})

            response = client.chat.completions.create(
                model=config.OPENAI_LLM_MODEL,
                messages=messages,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        else:
            # Default: Google Gemini API (Free Tier with Fallback loop)
            client = genai.Client(api_key=api_key)
            full_prompt = f"System Instruction: {system_instruction}\n\n{prompt_content}"
            
            models_to_try = [config.GEMINI_LLM_MODEL] + [
                m for m in config.GEMINI_FALLBACK_MODELS if m != config.GEMINI_LLM_MODEL
            ]

            last_error = None
            for model_name in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=full_prompt
                    )
                    if response and response.text:
                        return response.text.strip()
                except Exception as e:
                    last_error = e
                    continue

            raise Exception(f"Failed to generate response: {str(last_error)}")
