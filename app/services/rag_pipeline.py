# app/services/rag_pipeline.py
from typing import Dict, Any, List
from app.services.retriever import hybrid_search
from app.services.llm_client import chat

SYS_PROMPT = """Bạn là trợ lý trả lời theo ngữ cảnh bài báo tiếng Việt.
Chỉ sử dụng thông tin từ CONTEXT để trả lời. Nêu rõ trích dẫn (articleId, chunk_idx) nếu có."""

def build_context(chunks: List[dict]) -> str:
    parts = []
    for c in chunks:
        parts.append(f"[A{c['articleId']}-C{c['chunk_idx']}] {c['text']}")
    return "\n".join(parts)

async def answer(question: str, article_id: int | None, filters: dict | None) -> dict:
    # Demo: trả về answer giả lập
    return {
        "answer": "Đây là câu trả lời demo. AI chưa kích hoạt.",
        "citations": []
    }
