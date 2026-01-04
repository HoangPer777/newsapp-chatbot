# app/clients/backend_client.py
import httpx
from typing import Optional, Dict, Any
from app.core.config import settings

async def get_article_by_id(article_id: int) -> Optional[Dict[str, Any]]:
    # Controller: @RequestMapping("/api/articles") -> /api/articles/{id}
    url = f"{settings.BACKEND_BASE}/api/articles/{article_id}"
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(url)
        if r.status_code == 200: return r.json()
        return None

# Nếu backend có endpoint trả chunks theo article:
async def get_chunks_by_article(article_id: int) -> list[dict]:
    url = f"{settings.BACKEND_BASE}/api/articles/{article_id}/chunks"
    async with httpx.AsyncClient(timeout=15) as c:
        try:
            r = await c.get(url)
            if r.status_code == 200: return r.json()
        except Exception: pass
        return []

async def get_all_articles_custom() -> list[dict]:
    # Try fetching list of articles from common endpoints
    # Adjust '/articles' if your Spring controller endpoint is different
    # Assumes valid JSON response list
    # url = f"{settings.BACKEND_BASE}/api/articles?sort=all" 
    url = f"{settings.BACKEND_BASE}/api/articles"
    async with httpx.AsyncClient(timeout=30) as c:
        try:
            r = await c.get(url)
            if r.status_code == 200: 
                data = r.json()
                # If paginated, might be inside 'content' key
                if isinstance(data, dict) and 'content' in data:
                    return data['content']
                if isinstance(data, list):
                    return data
        except Exception as e:
            print(f"Error fetching all articles: {e}")
        return []
