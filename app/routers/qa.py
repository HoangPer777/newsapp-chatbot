# app/routers/qa.py
from fastapi import APIRouter, HTTPException
from app.models.schemas import QAReq, QAOut
from app.services.rag_pipeline import answer

router = APIRouter()

@router.post("", response_model=QAOut)
async def qa(req: QAReq):
    if not req.question.strip():
        raise HTTPException(400, "question is empty")
    res = await answer(req.question, req.articleId, req.filters or {})
    return QAOut(**res)
