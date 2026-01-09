from fastapi import APIRouter, BackgroundTasks
from app.clients.backend_client import get_all_articles_custom, get_article_by_id
from app.core.config import settings
from app.services.embedder import encode
import psycopg2
import time

router = APIRouter()

@router.post("/sync")
async def sync_data(background_tasks: BackgroundTasks):
    """
    Trigger background sync of articles. Returns immediately.
    """
    background_tasks.add_task(sync_data_worker)
    return {"message": "Sync started in background. Check server logs for progress."}

@router.post("/{article_id}")
async def ingest_article(article_id: int):
    """
    Ingest a single article by ID. Fetches data from backend and embeds it.
    """
    try:
        # Fetch from backend
        article_data = await get_article_by_id(article_id)
        if not article_data:
            return {"error": f"Article {article_id} not found in backend."}

        conn = psycopg2.connect(settings.PG_DSN)
        success = _process_and_store_article(conn, article_data)
        conn.close()
        
        if success:
            return {"message": f"Article {article_id} ingested successfully."}
        else:
            return {"message": f"Article {article_id} skipped (too short, exists, or error)."}
            
    except Exception as e:
        return {"error": str(e)}

def _process_and_store_article(conn, art: dict):
    cur = conn.cursor()
    
    # Check exist
    cur.execute("SELECT id FROM article_chunks WHERE article_id = %s LIMIT 1", (art['id'],))
    if cur.fetchone(): 
        # Optional: update logic could go here. For now, skip if exists.
        return False
    
    text = art.get('content') or art.get('contentPlain') or ""
    if len(text) < 10: return False
    
    # Truncate to be safe for embedding limit
    search_text = f"{art.get('title')} {art.get('summary') or ''} {text[:8000]}"
    
    # Retry loop
    max_retries = 3
    vector = None
    for attempt in range(max_retries):
        try:
            vector = encode([search_text])[0]
            break # Success
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                print(f"Rate limit hit at article {art['id']}. Waiting 10s...")
                import time
                time.sleep(10)
            else:
                print(f"Error embedding article {art['id']}: {e}")
                vector = None
                break
    
    if vector is None: return False

    cur.execute(
        "INSERT INTO article_chunks (article_id, chunk_text, embedding) VALUES (%s, %s, %s)",
        (art['id'], search_text, str(vector))
    )
    conn.commit()
    return True

async def sync_data_worker():
    print("Starting background sync...")
    try:
        from app.clients.backend_client import get_all_articles_custom
        articles = await get_all_articles_custom()
        
        if not articles:
            print("No articles found to sync.")
            return

        conn = psycopg2.connect(settings.PG_DSN)
        cur = conn.cursor()
        
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS article_chunks (
                id SERIAL PRIMARY KEY,
                article_id INT,
                chunk_text TEXT,
                embedding vector(768)
            );
        """)
        #embedding vector(384); -- Thay đổi nếu dùng mô hình khác
        conn.commit()
        
        count = 0
        total = len(articles)
        print(f"Found {total} articles. Processing...")

        for i, art in enumerate(articles):
            try:
                if _process_and_store_article(conn, art):
                    count += 1
                    # Nghỉ 2 giây sau mỗi bài để tránh bị Google báo 429
                    time.sleep(2)
                
                if count % 10 == 0:
                    print(f"Synced {count} articles...")

            except Exception as e:
                print(f"Error processing item {i}: {e}")
                continue
            
        conn.close()
        print(f"Sync complete. Total new: {count}")
        
    except Exception as e:
        print(f"Background sync error: {e}")
