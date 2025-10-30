# app/services/summarize_pipeline.py
from textwrap import wrap
from app.services.llm_client import chat

SYS = "Bạn là trợ lý tóm tắt báo tiếng Việt, giữ ý chính, trung lập, ngắn gọn."

def split_chunks(text: str, max_chars=2000):
    # đơn giản: chia theo ký tự; có thể thay bằng tokenizer
    return [t for t in wrap(text, max_chars) if t.strip()]

async def summarize_text(content: str, length: str = "short") -> str:
    # Demo version: trả về nội dung tóm tắt giả lập
    return "Tóm tắt demo: chức năng AI chưa kích hoạt."
