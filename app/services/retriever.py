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
        sql_params.append(settings.TOP_K_VEC) # for Limit
        
        query_sql = f"""
            SELECT article_id, chunk_text, 1 - (embedding <=> %s::vector) as score
            FROM article_chunks
            {where_str}
            ORDER BY embedding <=> %s::vector
            LIMIT %s;
        """
        
        # Correct params alignment:
        # 1. <=> %s in SELECT (optional, for score) -> we used %s inside select? 
        # Actually standard pgvector usage:
        # ORDER BY embedding <=> '[...]'
        
        # Simplified query to avoid parameter confusion:
        cur.execute(f"""
            SELECT article_id, chunk_text, 1 - (embedding <=> %s::vector) as score
            FROM article_chunks
            {where_str}
            ORDER BY embedding <=> %s::vector
            LIMIT %s;
        """, (vec_str, *sql_params))
        
        rows = cur.fetchall()
        conn.close()
        
        # 3. Format Output
        out = []
        for r in rows:
            # r = (article_id, chunk_text, score)
            out.append({
                "articleId": r[0],
                "chunk_idx": 0, # we didn't store idx effectively, 0 is placeholder
                "text": r[1],
                "score": float(r[2])
            })
            
        return out

    except Exception as e:
        print(f"pgvector search error: {e}")
        return []