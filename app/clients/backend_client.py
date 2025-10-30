# app/clients/backend_client.py
import httpx
from typing import Optional, Dict, Any
from app.core.config import settings

async def get_article_by_id(article_id: int) -> Optional[Dict[str, Any]]:
    url = f"{settings.BACKEND_BASE}/articles/{article_id}"
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(url)
        if r.status_code == 200: return r.json()
        return None

# Nếu backend có endpoint trả chunks theo article:
async def get_chunks_by_article(article_id: int) -> list[dict]:
    url = f"{settings.BACKEND_BASE}/articles/{article_id}/chunks"
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get(url)
        if r.status_code == 200: return r.json()
        return []
