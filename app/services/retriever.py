# app/services/retriever.py 
import psycopg2
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from app.core.config import settings
from app.services.embedder import encode

def _get_conn():
    return psycopg2.connect(settings.PG_DSN)

def hybrid_search(query: str, article_id: Optional[int], filters: Optional[Dict[str, Any]]) -> List[dict]:
    try:
        # 1. Embed Query
        qv = encode([query])[0]
        vec_str = str(list(qv)) # Đảm bảo định dạng '[0.1, 0.2, ...]'
        
        conn = _get_conn()
        cur = conn.cursor()
        
        # 2. Xây dựng tham số SQL theo ĐÚNG THỨ TỰ xuất hiện của %s
        # Thứ tự trong Execute: [1. vec_str cho Score, 2. article_id cho WHERE (nếu có), 3. vec_str cho ORDER BY, 4. LIMIT]
        
        where_clause = ""
        params = [vec_str] # %s đầu tiên cho 'score'
        
        if article_id and article_id != 0:
            where_clause = "WHERE ac.article_id = %s"
            params.append(article_id) # %s thứ hai
            
        params.append(vec_str) # %s thứ ba cho ORDER BY
        params.append(50)      # %s thứ tư cho LIMIT

        cur.execute(f"""
            SELECT 
                ac.article_id, 
                ac.chunk_text, 
                COALESCE(1 - (ac.embedding <=> %s::vector), 0) as score,
                a.title,         -- (r[3])
                a.image_url,     -- (r[4])
                a.category,      -- (r[5])
                a.created_at,    -- (r[6])
                u.display_name   -- (r[7])
            FROM article_chunks ac
            JOIN articles a ON ac.article_id = a.id
            LEFT JOIN users u ON a.author_id = u.id
            {where_clause}
            ORDER BY ac.embedding <=> %s::vector
            LIMIT %s;
        """, tuple(params))
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        # 3. Format Output
        out = []
        seen_ids = set()
        for r in rows:
            a_id = r[0]
            if a_id in seen_ids:
                continue
            seen_ids.add(a_id)

            out.append({
                "article_id": a_id,
                "chunk_text": r[1],
                "score": float(r[2]),
                "title": r[3],
                "image_url": r[4],
                "category": r[5] if r[5] else "",
                "published_at": r[6].isoformat() if r[6] else "",
                "author_name": r[7] if r[7] else "Unknown"
            })
            
        return out

    except Exception as e:
        print(f"pgvector search error: {e}")
        return []