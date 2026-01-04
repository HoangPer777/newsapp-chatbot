# app/routers/qa.py
from fastapi import APIRouter, HTTPException
from app.models.schemas import QAReq, QAOut
from app.services.rag_pipeline import answer
from app.services.retriever import hybrid_search
from app.clients.backend_client import get_article_by_id

router = APIRouter()

@router.post("", response_model=QAOut)
async def qa(req: QAReq):
    """
    Q&A using Vector RAG (pgvector).
    1. If articleId provided -> Search relevant chunks within that article.
    2. Retrieve Context.
    3. Generate Answer.
    """
    if not req.question.strip():
        raise HTTPException(400, "question is empty")

    context = ""
    citations = []

    # STRATEGY 1: VECTOR SEARCH (RAG)
    # Search for relevant chunks in pgvector (filtered by articleId if present)
    # This is better than reading the whole article if the article is long.
    relevant_chunks = hybrid_search(req.question, article_id=req.articleId, filters=req.filters)
    
    if relevant_chunks:
        # Construct context from top chunks
        context_parts = [c['chunk_text'] for c in relevant_chunks]
        context = "\n\n...\n\n".join(context_parts)
        
        # citations = [f"Text match (Score: {c['score']:.2f})" for c in relevant_chunks]
    # SỬA Ở ĐÂY: Thay vì chỉ lưu text, hãy lưu article_id của từng chunk
        # Dùng set() để tránh trùng lặp nếu nhiều chunk thuộc cùng 1 bài báo
        seen_ids = set()
        for c in relevant_chunks:
            aid = c.get('article_id')
            if aid and aid not in seen_ids:
                citations.append(f"article_id:{aid}") # Định dạng đặc biệt để Flutter dễ nhận biết
                seen_ids.add(aid)
    # STRATEGY 2: FALLBACK TO FULL CONTENT (CONTEXT STUFFING)
    # If vector search returns nothing (maybe article not ingested yet?), fetch full content from backend
    if not context and req.articleId:
        try:
            article = await get_article_by_id(req.articleId)
            if article:
                context = article.get("content") or article.get("contentPlain") or ""
        except Exception as e:
            print(f"Fallback fetch error: {e}")

    if not context:
        # If still no context, we can't answer strictly based on article
        # But maybe we try to answer generally? Or return error?
        # Requirement says "Chat with article", so better return "I don't know".
        pass

    # Call LLM
    # res = await answer(
    #     question=req.question,
    #     article_id=req.articleId,
    #     filters=req.filters,
    #     context=context
    # )
    res = await answer(
        question=req.question,
        chunks=relevant_chunks, # Truyền cái List Dictionary vừa lấy được
        context=context
    )
    
    # Merge citations if any
    # (The answer function might return generic citations, we can enhance them)
    # If using vector RAG, we trust the vector chunks more.
    
    return QAOut(
        answer=res['answer'],
        citations=citations if citations else res['citations']
    )
