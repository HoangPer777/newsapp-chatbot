# app/services/llm_client.py
# from openai import OpenAI
from app.core.config import settings

# _client = OpenAI(
#     api_key=settings.OPENAI_API_KEY or None,
#     base_url=settings.OPENAI_API_BASE
# )

async def chat(messages: list[dict], model: str | None = None) -> str:
    # Demo version: mock response, no openai call!
    return "[Demo only: chưa tích hợp AI trả lời]"

def embed_texts(texts: list[str]) -> list[list[float]]:
    # Demo version: trả về vector 0
    return [[0.0 for _ in range(settings.EMBED_DIM)] for _ in texts]
