import math
from fastapi import APIRouter, HTTPException
from app.models.schemas import QAReq, QAOut, RelatedSource
from app.services.rag_pipeline import answer
from app.services.retriever import hybrid_search
from app.clients.backend_client import get_article_by_id
from app.core.config import settings


router = APIRouter()

@router.post("", response_model=QAOut)
async def qa(req: QAReq):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Câu hỏi không được để trống")

    context = ""
    related_sources = []
    seen_ids = set()
    relevant_chunks = []
    valid_texts_for_context = []

    # 1. Tìm kiếm dữ liệu từ Vector DB
    try:
        search_id = req.articleId if (req.articleId and req.articleId != 0) else None
        relevant_chunks = hybrid_search(req.question, article_id=search_id, filters=req.filters)
        print(f"DEBUG: Tìm thấy {len(relevant_chunks)} đoạn văn từ DB")
    except Exception as e:
        print(f"Lỗi Vector Search: {e}")
        relevant_chunks = []

        
        # 2. Xử lý logic lọc, cứu bài nan và tạo Context
    if relevant_chunks:
        SCORE_THRESHOLD = 0.3 # Ngưỡng lọc bài rác
        all_potential_sources = []
        query_clean = req.question.lower().strip()
        
        # Lấy danh sách các từ trong câu hỏi để so khớp
        query_words = [word.lower() for word in query_clean.split() if len(word) >= 2]

        for c in relevant_chunks:
            aid = c.get('article_id')
            raw_score = c.get('score')
            
            # Xử lý điểm số NaN hoặc None
            if raw_score is None or (isinstance(raw_score, float) and math.isnan(raw_score)):
                final_score = 0.0
            else:
                final_score = float(raw_score)

            chunk_text = c.get('chunk_text', '')
            chunk_text_lower = chunk_text.lower()

            # --- LOGIC BOOSTING TỪ KHÓA ---
            # Chỉ thưởng điểm nếu từ trong câu hỏi xuất hiện trong nội dung bài báo
            match_count = sum(1 for word in query_words if word in chunk_text_lower)
            # if match_count > 0:
            if match_count <= 0:
                final_score -= 0.5 
            else:
                # Mỗi từ khớp thưởng 0.2 điểm
                final_score += (match_count * 0.2)
                # print(f"--> Boosting cho bài {aid}: {match_count} từ khớp. Điểm mới: {final_score}")


            # Kiểm tra bài viết có vượt qua ngưỡng lọc không
            if final_score >= SCORE_THRESHOLD:
                valid_texts_for_context.append(chunk_text)
                if aid and aid not in seen_ids:
                    all_potential_sources.append(RelatedSource(
                        id=aid,
                        title=chunk_text.split('\n')[0][:100] or "Bài viết liên quan",
                        link=f"{settings.ARTICLE_DETAIL_BASE_URL}/{aid}",
                        score=final_score
                    ))
                    seen_ids.add(aid)

        # Sắp xếp và lấy 3 nguồn liên quan nhất
        all_potential_sources.sort(key=lambda x: x.score, reverse=True)
        related_sources = all_potential_sources[:3] 

        if valid_texts_for_context:
            context = "\n\n---\n\n".join(valid_texts_for_context)

    # 3. Fallback
    if not context and req.articleId and req.articleId != 0:
        try:
            article = await get_article_by_id(req.articleId)
            if article:
                context = article.get("content") or article.get("contentPlain") or ""
                related_sources = [RelatedSource(
                    id=req.articleId,
                    title=article.get("title", "Bài báo hiện tại"),
                    link=f"{settings.ARTICLE_DETAIL_BASE_URL}/{req.articleId}",
                    # link=f"http://10.0.2.2:8080/api/articles/{req.articleId}",
                    score=1.0
                )]
        except Exception as e:
            print(f"Lỗi Fallback: {e}")

    # 4. Kiểm tra context trống
    if not context.strip():
        context = "Không tìm thấy bài báo nào liên quan. Nếu đây là câu hỏi xã giao, hãy trả lời bình thường. Nếu là câu hỏi kiến thức, hãy báo là không có dữ liệu."
    
    # 5. Gọi AI trả lời
    try:
        res = await answer(question=req.question, chunks=relevant_chunks, context=context)
        final_answer = res.get('answer', '')
        
        # Danh sách các câu "từ chối" của AI khi KHÔNG tìm thấy kiến thức trong bài báo
        no_info_signals = ["không tìm thấy", "không có thông tin", "không đề cập", "tôi không biết"]
        
        # LOGIC QUYẾT ĐỊNH HIỆN LINK:
        # Nếu AI trả lời xã giao (Chào bạn...) thì final_answer sẽ không chứa các từ khóa từ chối trên.
        # Nhưng vì context trống, related_sources lúc này vốn dĩ đã là [] (mảng rỗng).
        
        is_no_info = any(sig in final_answer.lower() for sig in no_info_signals)
        
        if is_no_info:
            final_sources = [] # Gõ rác "dsjfh" -> AI báo không thấy -> Xóa link
        else:
            final_sources = related_sources # Gõ "AI", "Spring" -> Thấy bài -> Hiện link

        return QAOut(
            answer=final_answer,
            related_articles=final_sources
        )
    except Exception as e:
        print(f"Lỗi AI: {e}")
        # Nếu AI lỗi (429...), cũng không hiện link lung tung
        return QAOut(answer=f"Lỗi hệ thống AI: {str(e)}", related_articles=[])