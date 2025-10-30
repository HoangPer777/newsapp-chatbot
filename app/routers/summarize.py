# app/routers/summarize.py
from fastapi import APIRouter, HTTPException
from app.models.schemas import SummarizeReq, SummaryOut
from app.clients.backend_client import get_article_by_id
from app.services.summarize_pipeline import summarize_text

router = APIRouter()

@router.post("", response_model=SummaryOut)
async def summarize(req: SummarizeReq):
    content = req.content
    aid = req.articleId
    citations: list[str] = []

    if not content and aid:
        art = await get_article_by_id(aid)
        if not art: raise HTTPException(404, "article not found")
        content = art.get("contentPlain") or art.get("content_plain") or art.get("content") or ""
        if not content: raise HTTPException(400, "no content to summarize")
        citations = [f"articleId:{aid}"]

    if not content and req.url:
        # TODO: fetch content by url (tùy bạn implement). Tạm thời trả lỗi:
        raise HTTPException(400, "fetch by url not implemented")

    if not content:
        raise HTTPException(400, "please provide articleId | url | content")

    summary = await summarize_text(content, req.length)
    return SummaryOut(summary=summary, articleId=aid, citations=citations)
