# app/services/retriever.py 
import psycopg2
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from app.core.config import settings
from app.services.embedder import encode

def _get_conn():
    return psycopg2.connect(settings.PG_DSN)

def hybrid_search(query: str, article_id: Optional[int], filters: Optional[Dict[str, Any]]) -> List[dict]:
    """
    Search using pgvector cosine distance.
    Currently only Vector search is implemented (Hybrid with BM25 requires more complex setup in Postgres or Python).
    
    Args:
        query: User question
        article_id: Filter by article (for Q&A context)
        filters: Additional filters
    """
    try:
        # 1. Embed Query
        qv = encode([query])[0]
        
        # 2. SQL Query
        # 1 - (embedding <=> qv) converts distance to similarity score
        conn = _get_conn()
        cur = conn.cursor()
        
        # Base query
        # We need to cast the list[float] to string representation for pgvector input: '[0.1, 0.2, ...]'
        vec_str = str(qv)
        
        where_clauses = []
        params = [vec_str] # for ORDER BY embedding <=> %s
        
        # Optional: Filter by article_id (if this is Q&A within an article context)
        # Note: If article_id is strictly provided, we might just want to return all chunks of that article?
        # But RAG usually scans relevancy.
        if article_id:
            where_clauses.append("article_id = %s")
            params.append(article_id)

        where_str = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        # Note: ORDER BY <-> requires the vector parameter again?
        # A common pattern: ORDER BY embedding <=> %s
        # params needs: [vec_str] (for order by) + [filters...]
        
        # Let's fix params order based on SQL structure:
        # SELECT ... FROM ... WHERE ... ORDER BY ... LIMIT ...
        
        sql_params = []
        if article_id: sql_params.append(article_id)
        
        sql_params.append(vec_str) # for Order By
        # sql_params.append(settings.TOP_K_VEC)
        sql_params.append(50) # Increased limit for client-side filtering
        
        # JOIN with articles to get full metadata
        # JOIN with users to get author name (Author entity merged into User)
        cur.execute(f"""
            SELECT 
                ac.article_id, 
                ac.chunk_text, 
                1 - (ac.embedding <=> %s::vector) as score,
                a.title,
                a.image_url,
                a.category,
                a.created_at,
                u.display_name
            FROM article_chunks ac
            JOIN articles a ON ac.article_id = a.id
            LEFT JOIN users u ON a.author_id = u.id
            {where_str}
            ORDER BY ac.embedding <=> %s::vector
            LIMIT %s;
        """, (vec_str, *sql_params))
        
        rows = cur.fetchall()
        conn.close()
        
        # 3. Format Output
        out = []
        seen_ids = set()
        for r in rows:
            # Deduplicate by article_id (since multiple chunks might match same article)
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