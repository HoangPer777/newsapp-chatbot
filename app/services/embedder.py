# app/services/embedder.py
from app.core.config import settings
import numpy as np

_model = None
_provider = settings.EMBED_PROVIDER

print(f"Loading embedding model: {_provider} ...")

if _provider == "hf":
    from sentence_transformers import SentenceTransformer
    _model = SentenceTransformer(settings.EMBED_MODEL_HF)

if _provider == "gemini":
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    # Note: langchain wrapper handles retries and async internally often, 
    # but we use synchronous invoke here for simplicity in this wrapper functions
    if not settings.GOOGLE_API_KEY:
        print("CRITICAL WARNING: GEMINI provider selected but GOOGLE_API_KEY missing.")
    
    _model = GoogleGenerativeAIEmbeddings(
        model=settings.EMBED_MODEL_GEMINI,
        google_api_key=settings.GOOGLE_API_KEY
    )

def encode(texts: list[str]) -> list[list[float]]:
    if not texts: return []
    
    try:
        # STRATEGY: HUGGINGFACE LOCAL
        if _provider == "hf":
            embeddings = _model.encode(texts, show_progress_bar=False)
            if isinstance(embeddings, np.ndarray):
                return embeddings.tolist()
            return embeddings

        # STRATEGY: GEMINI (GOOGLE)
        elif _provider == "gemini":
            # Langchain Embeddings.embed_documents(texts) -> list[list[float]]
            return _model.embed_documents(texts)
            
        else:
            return []

    except Exception as e:
        print(f"Embedding error ({_provider}): {e}")
        # Fallback to zero vector
        return [[0.0] * settings.EMBED_DIM for _ in texts]
