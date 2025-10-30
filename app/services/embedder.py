# app/services/embedder.py
from app.services.llm_client import embed_texts
from app.core.config import settings

def encode(texts: list[str]) -> list[list[float]]:
    # Demo: trả về vector 0
    return [[0.0 for _ in range(settings.EMBED_DIM)] for _ in texts]
