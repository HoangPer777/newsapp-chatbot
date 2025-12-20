# app/routers/search.py
from fastapi import APIRouter
from app.services.retriever import hybrid_search
from pydantic import BaseModel

router = APIRouter()

class SearchReq(BaseModel):
    query: str
    limit: int = 10

@router.post("")
def search(req: SearchReq):
    # Retrieve using pgvector logic (via hybrid_search wrapper)
    results = hybrid_search(req.query, article_id=None, filters=None)
    
    # Return mapping
    # Usually we want to return article IDs so frontend can navigate.
    return {
        "query": req.query,
        "results": results
    }
