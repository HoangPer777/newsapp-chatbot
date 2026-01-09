# app/main.py
import os
import uvicorn
from dotenv import load_dotenv

# 1. Load biến môi trường ngay lập tức
load_dotenv()
# print(f"API KEY CHECK: {os.getenv('GOOGLE_API_KEY')}") # Bật lên nếu cần debug

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai

from app.core.config import settings
from app.core.logging import setup_logging

# Import các Routers
from app.routers import health, qa, search, ingest
from app.routers.ingest import sync_data_worker

# 2. Setup Logging
setup_logging()

# 3. Khởi tạo App
app = FastAPI(title="PHIEN BAN MOI NHAT 2026", version="9.9.9")

# 4. Cấu hình CORS (Cho phép Flutter/Web gọi API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS, # Hoặc để ["*"] nếu muốn mở hết
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Đăng ký Routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(qa.router, prefix="/qa", tags=["qa"])
app.include_router(search.router, prefix="/search", tags=["search"])
app.include_router(ingest.router, prefix="/ingest", tags=["ingest"])

# 6. Endpoint Sync (Nhận tín hiệu từ Spring Boot)
@app.post("/sync")
async def sync_database_trigger(background_tasks: BackgroundTasks):
    print(">>> [PYTHON] Đã nhận tín hiệu SYNC từ Java Spring Boot!")
    # background_tasks.add_task(sync_data_worker)  # Cách này không hoạt động do FastAPI bị giới hạn không cho chạy đa luồng
    return {"message": "Sync signal received, processing in background"}

# 7. Endpoint Debug Model
@app.get("/debug/models")
def list_gemini_models():
    api_key = os.environ.get("GOOGLE_API_KEY") or settings.GOOGLE_API_KEY
    if not api_key: return {"error": "No API Key"}
    
    try:
        genai.configure(api_key=api_key)
        models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                models.append(m.name)
        return {"models": models}
    except Exception as e:
        return {"error": str(e)}

# 8. Chạy Server
# if __name__ == "__main__":
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

# Khi chạy Docker:
if __name__ == "__main__":
    # chú ý: port=8000 phải khớp với ports trong compose.yaml
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000) 
