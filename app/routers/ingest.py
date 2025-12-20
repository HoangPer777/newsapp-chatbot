# app/routers/ingest.py
from fastapi import APIRouter
from app.clients.backend_client import get_all_articles_custom
from app.services.embedder import encode
from app.core.config import settings
import psycopg2

router = APIRouter()

@router.post("/sync")
async def sync_data():
    """
    Fetch all articles from backend and ingest into pgvector.
    Creates table if not exists.
    """
    try:
        # 1. Fetch data
        # Note: You need to ensure get_all_articles() is implemented in backend_client.py
        # Current backend_client.py likely only has get_article_by_id.
        # We'll need to double check or mock it.
        # For now, let's assume we can fetch list.
        # IF backend doesn't support list all, we might fail here.
        
        # Temporary: To make it work immediately without modifying backend java code significantly,
        # we might need to rely on what's available or ask user to provide list.
        # Assuming the backend has GET /articles endpoint (common in REST).
        from app.clients.backend_client import get_all_articles_custom
        articles = await get_all_articles_custom()
        
        if not articles:
            return {"message": "No articles found or backend unreachable"}

        # 2. Connect DB
        conn = psycopg2.connect(settings.PG_DSN)
        cur = conn.cursor()
        
        # 3. Create extension and table
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        conn.commit()
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS article_chunks (
                id SERIAL PRIMARY KEY,
                article_id INT,
                chunk_text TEXT,
                embedding vector(768)
            );
        """)
        conn.commit()
        
        # 4. Clear old data? (Optional, or just append distinct)
        # cur.execute("TRUNCATE TABLE article_chunks;") 
        
        # 5. Ingest
        count = 0
        for art in articles:
            # Check if exists to avoid dups (naive check)
            cur.execute("SELECT id FROM article_chunks WHERE article_id = %s LIMIT 1", (art['id'],))
            if cur.fetchone(): continue
            
            text = art.get('content') or art.get('contentPlain') or ""
            if len(text) < 10: continue
            
            # Smart Chunking (simple version: split by 500 chars)
            # Better: Use langchain RecursiveCharacterTextSplitter if available
            # But to keep dependencies low, naive split ok for now or full text if short.
            # Assuming 'context stuffing' style for Q&A, we might want full text if not too long.
            # But for SEARCH, full text vector might be diluted.
            # Let's simple split.
            
            # For this MVP, let's just store the TITLE + SUMMARY + first 1000 chars of CONTENT for search
            # This is efficient for retrieval.
            
            # IMPORTANT for Gemini Embedding: Input text limit is often ~2048 tokens or 10k chars.
            # We must be safe.
            search_text = f"{art.get('title')} {art.get('summary') or ''} {text[:8000]}"
            vector = encode([search_text])[0]
            
            cur.execute(
                "INSERT INTO article_chunks (article_id, chunk_text, embedding) VALUES (%s, %s, %s)",
                (art['id'], search_text, str(vector))
            )
            count += 1
            
            # Throttle if using Cloud Embeddings (Gemini Free Tier has rate limits)
            if settings.EMBED_PROVIDER == "gemini":
                import time
                time.sleep(2) # Wait 2s between requests to be safe
            
        conn.commit()
        conn.close()
        return {"message": f"Synced {count} new articles to pgvector"}
        
    except Exception as e:
        print(f"Ingest error: {e}")
        return {"error": str(e)}
