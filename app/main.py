# app/main.py
import os
from dotenv import load_dotenv
load_dotenv()  # Nạp API Key từ file .env ngay lập tức
print(f"API KEY CHECK: {os.getenv('GOOGLE_API_KEY')}")
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.routers import health, qa

from app.routers.ingest import sync_data_worker

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

from fastapi import BackgroundTasks

@app.post("/sync")
async def sync_database_trigger(background_tasks: BackgroundTasks):
    print(">>> [PYTHON] Đã nhận tín hiệu SYNC từ Java Spring Boot!")
    
    # Ở đây Han sẽ gọi hàm logic để đồng bộ dữ liệu
    # Ví dụ: import hàm sync từ service
    # from app.services.embedding_service import run_sync_process
    # background_tasks.add_task(run_sync_process) 
    background_tasks.add_task(sync_data_worker)
    return {"message": "Sync signal received, processing in background"}

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
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)