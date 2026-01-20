# app/clients/backend_client.py
import httpx
from typing import Optional, Dict, Any
from app.core.config import settings

async def get_article_by_id(article_id: int) -> Optional[Dict[str, Any]]:
    # Controller: @RequestMapping("/api/articles") -> /api/articles/{id}
    url = f"{settings.BACKEND_BASE}/api/articles/{article_id}"
    
    headers = {
        "Authorization": f"Bearer {settings.JAVA_ACCESS_TOKEN}"    }

    async with httpx.AsyncClient(timeout=10) as c:
        try:
            r = await c.get(url, headers=headers)
            if r.status_code == 200: 
                return r.json()
            else:
                print(f"[DEBUG] Lỗi lấy bài ID {article_id}: Status {r.status_code} - {r.text}")
        except Exception as e:
            print(f"[ERROR] Lỗi kết nối lấy bài {article_id}: {e}")
            
    return None

async def get_chunks_by_article(article_id: int) -> list[dict]:
    url = f"{settings.BACKEND_BASE}/api/articles/{article_id}/chunks"
    headers = {"Authorization": f"Bearer {settings.JAVA_ACCESS_TOKEN}"}
    
    async with httpx.AsyncClient(timeout=15) as c:
        try:
            r = await c.get(url, headers=headers)
            if r.status_code == 200: return r.json()
        except Exception: pass
        return []

async def get_all_articles_custom() -> list[dict]:
    # Kiểm tra settings.BACKEND_BASE xem đã đúng là http://host.docker.internal:8080 chưa (nếu chạy Docker)
    url = f"{settings.BACKEND_BASE}/api/articles"
    # url = f"http://localhost:8080/api/articles"
    
    headers = {
        "Authorization": f"Bearer {settings.JAVA_ACCESS_TOKEN}"
    }

    print(f"--- Đang gọi API: {url} ---")

    async with httpx.AsyncClient(timeout=30) as c:
        try:
            r = await c.get(url, headers=headers)
            
            if r.status_code == 200: 
                data = r.json()
                print(f"--- Thành công! Lấy được dữ liệu ---")
                
                # Xử lý phân trang Spring Boot 
                if isinstance(data, dict) and 'content' in data:
                    return data['content']
                if isinstance(data, list):
                    return data
            else:
                # IN RA LỖI ĐỂ BIẾT TẠI SAO KHÔNG LẤY ĐƯỢC
                print(f"--- THẤT BẠI ---")
                print(f"Status Code: {r.status_code}") # 401 là sai Token, 404 là sai Link
                print(f"Response: {r.text}")

        except Exception as e:
            print(f"--- LỖI KẾT NỐI (Connection Error) ---")
            print(f"Chi tiết: {e}")
            print("Gợi ý: Kiểm tra xem Backend có đang chạy không? URL có đúng localhost/host.docker.internal chưa?")
            
        return []