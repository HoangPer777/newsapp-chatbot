# app/models/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List

class SummarizeReq(BaseModel):
    articleId: Optional[int] = None
    url: Optional[str] = None
    content: Optional[str] = None
    length: str = Field(default="short", pattern="^(short|medium|long)$")

class SummaryOut(BaseModel):
    summary: str
    articleId: Optional[int] = None
    citations: List[str] = []

class QAReq(BaseModel):
    question: str
    articleId: Optional[int] = None
    filters: Optional[dict] = None

class Citation(BaseModel):
    articleId: int
    chunk_idx: int
    text: str

class QAOut(BaseModel):
    answer: str
    citations: List[Citation] = []
