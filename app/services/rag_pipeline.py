# app/services/rag_pipeline.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.services.llm_client import llm

# 1. Define the Prompt
qa_prompt = ChatPromptTemplate.from_messages([
    ("system", "Bạn là một trợ lý AI hữu ích cho ứng dụng đọc báo NewsApp. Nhiệm vụ của bạn là trả lời câu hỏi dựa trên nội dung bài báo. Nếu bài báo không chứa thông tin, hãy nói rõ là không tìm thấy."),
    ("user", """
Dựa trên các đoạn văn sau từ bài báo:
<NGỮ CẢNH>
{context}
</NGỮ CẢNH>

Câu hỏi của tôi: {question}

Trả lời (ngắn gọn, đúng trọng tâm):
""")
])

# 2. Create the Chain
qa_chain = qa_prompt | llm | StrOutputParser()

async def answer(question: str, article_id: int | None, filters: dict | None, context: str = "") -> dict:
    
    if not context:
        return {
            "answer": "Xin lỗi, tôi không tìm thấy thông tin phù hợp trong bài báo để trả lời.",
            "citations": []
        }

    try:
        answer_text = await qa_chain.ainvoke({
            "context": context,
            "question": question
        })

        return {
            "answer": answer_text,
            "citations": [] # Citations handled by caller (router) based on chunks
        }
    except Exception as e:
        print(f"RAG Error: {e}")
        return {
            "answer": f"Lỗi xử lý AI: {str(e)}",
            "citations": []
        }
