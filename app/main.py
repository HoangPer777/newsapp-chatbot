# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.routers import health, qa

setup_logging()

app = FastAPI(title=settings.APP_NAME, version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, prefix="/health", tags=["health"])

app.include_router(qa.router, prefix="/qa", tags=["qa"])
from app.routers import search, ingest
app.include_router(search.router, prefix="/search", tags=["search"])
app.include_router(ingest.router, prefix="/ingest", tags=["ingest"])

@app.get("/debug/models")
def list_gemini_models():
    import google.generativeai as genai
    import os
    
    api_key = os.environ.get("GOOGLE_API_KEY") or settings.GOOGLE_API_KEY
    if not api_key: return {"error": "No API Key"}
    
    genai.configure(api_key=api_key)
    models = []
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                models.append(m.name)
    except Exception as e:
        return {"error": str(e)}
        
    return {"models": models}
