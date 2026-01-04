# app/services/rag_pipeline.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.services.llm_client import llm

# 1. Define the Prompt
qa_prompt = ChatPromptTemplate.from_messages([
    ("system", """Bạn là trợ lý AI cho NewsApp. 
    Nhiệm vụ: Trả lời câu hỏi dựa trên nội dung bài báo.
    Yêu cầu quan trọng: Bạn PHẢI trích xuất chính xác 'article_id' từ ngữ cảnh được cung cấp.
    Nếu có nhiều bài báo, hãy ưu tiên bài báo có nội dung sát nhất."""),
    ("user", """
Dựa trên các đoạn văn sau (Mỗi đoạn bắt đầu bằng ID bài báo):
{context}

Câu hỏi: {question}

Hãy trả lời ngắn gọn và kèm theo ID bài báo bạn đã dùng để trả lời theo định dạng: (ID: X)
""")
])
# qa_prompt = ChatPromptTemplate.from_messages([
#     ("system", "Bạn là một trợ lý AI hữu ích cho ứng dụng đọc báo NewsApp. Nhiệm vụ của bạn là trả lời câu hỏi dựa trên nội dung bài báo. Nếu bài báo không chứa thông tin, hãy nói rõ là không tìm thấy."),
#     ("user", """
# Dựa trên các đoạn văn sau từ bài báo:
# <NGỮ CẢNH>
# {context}
# </NGỮ CẢNH>

# Câu hỏi của tôi: {question}

# Trả lời (ngắn gọn, đúng trọng tâm):
# """)
# ])

# 2. Create the Chain
qa_chain = qa_prompt | llm | StrOutputParser()

# async def answer(question: str, article_id: int | None, filters: dict | None, context: str = "") -> dict:
    
#     if not context:
#         return {
#             "answer": "Xin lỗi, tôi không tìm thấy thông tin phù hợp trong bài báo để trả lời.",
#             "citations": []
#         }

#     try:
#         answer_text = await qa_chain.ainvoke({
#             "context": context,
#             "question": question
#         })

#         return {
#             "answer": answer_text,
#             "citations": [] # Citations handled by caller (router) based on chunks
#         }
#     except Exception as e:
#         print(f"RAG Error: {e}")
#         return {
#             "answer": f"Lỗi xử lý AI: {str(e)}",
#             "citations": []
#         }


async def answer(question: str, chunks: list, context: str = "") -> dict:
    if not context:
        return {"answer": "Không tìm thấy thông tin phù hợp.", "citations": []}

    try:
        answer_text = await qa_chain.ainvoke({"context": context, "question": question})

        # Tạo danh sách trích dẫn từ các chunks tìm được
        citations = []
        if chunks:
            # Chỉ lấy article_id của bài báo đầu tiên (liên quan nhất)
            # để đảm bảo nút "Xem bài báo" dẫn đúng về nguồn chính.
            aid = chunks[0].get('article_id')
            if aid:
                # Trả về định dạng mà Flutter của Han đang chờ: "article_id:33"
                citations.append(f"article_id:{aid}")
        # seen_ids = set()
        # for c in chunks:
        #     # c[0] thường là article_id, c[1] là text (tùy vào retriever.py của Han)
        #     aid = c.get('article_id')
        #     if aid and aid not in seen_ids:
        #         citations.append({"article_id": aid})
        #         seen_ids.add(aid)

        return {
            "answer": answer_text,
            "citations": citations 
        }
    except Exception as e:
        print(f"RAG Error: {e}")
        return {"answer": f"Lỗi AI: {str(e)}", "citations": []}