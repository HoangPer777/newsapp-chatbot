# app/services/llm_client.py
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
import os

# Initialize LLM (Gemini)
if not settings.GOOGLE_API_KEY:
    print("WARNING: GOOGLE_API_KEY is not set. Chatbot features will fail.")

llm = ChatGoogleGenerativeAI(
    model=settings.LLM_MODEL,
    google_api_key=settings.GOOGLE_API_KEY,
    temperature=0.3, # Low temperature for factual RAG
    convert_system_message_to_human=True,
    max_retries=5 
)

async def chat(messages: list[dict], model: str | None = None) -> str:
    """
    Simple wrapper for non-RAG chat (e.g. summarization).
    messages: list of {"role": "user"/"system", "content": "..."}
    """
    try:
        from langchain_core.messages import HumanMessage, SystemMessage
        
        lc_messages = []
        for m in messages:
            if m["role"] == "system":
                lc_messages.append(SystemMessage(content=m["content"]))
            else:
                lc_messages.append(HumanMessage(content=m["content"]))
                
        resp = await llm.ainvoke(lc_messages)
        return resp.content
    except Exception as e:
        print(f"LLM Chat Error: {e}")
        return "Xin lỗi, chức năng AI đang gặp sự cố kết nối."

# Embed texts stub (since we use separate embedder or sentence-transformers)
async def embed_texts(texts: list[str], model: str | None = None) -> list[list[float]]:
    # We are using app/services/embedder.py with local model now.
    # This might be deprecated or unused, but keeping stub for safety.
    return []
