# app/services/rag_pipeline.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.services.llm_client import llm

# # 1. Define the Prompt
# qa_prompt = ChatPromptTemplate.from_messages([
#     ("system", """You are an expert news assistant for NewsApp.
#     Task: Answer questions or SUMMARIZE articles based on the provided context.
    
#     If the user asks for a summary:
#     - Provide a concise summary of the main points.
#     - Use bullet points if there are multiple key facts.
#     - Keep the tone professional.
    
#     Language Policy: Respond in the SAME LANGUAGE as the user's question.
#     Requirement: You MUST extract the exact 'article_id' from the context."""),
    
#     ("user", """
# Context:
# {context}

# Question: {question}

# Answer:""")
# ])
# 1. Define the Prompt
qa_prompt = ChatPromptTemplate.from_messages([
    ("system", """Bạn là một trợ lý tin tức thông minh và thân thiện của NewsApp.

    NHIỆM VỤ:
    1. Nếu người dùng chào hỏi (ví dụ: Hello, Hi, Chào bạn) hoặc hỏi những câu xã giao không liên quan đến tin tức: Hãy đáp lại một cách thân thiện và ngắn gọn.
    2. Nếu người dùng hỏi về thông tin trong bài báo: Hãy sử dụng Context được cung cấp để trả lời chính xác.
    3. Nếu người dùng yêu cầu TÓM TẮT (Summarize): Hãy tóm tắt các ý chính dưới dạng gạch đầu dòng.

    QUY TẮC:
    - Nếu thông tin KHÔNG có trong Context và cũng KHÔNG phải là câu hỏi xã giao: Hãy trả lời là "Tôi không tìm thấy thông tin này trong hệ thống dữ liệu bài báo".
    - Luôn trả lời bằng NGÔN NGỮ mà người dùng sử dụng để hỏi.
    - Giữ tông giọng chuyên nghiệp nhưng gần gũi."""),
    
    ("user", """
Ngữ cảnh (Context):
{context}

Câu hỏi: {question}

Trả lời:""")
])
# 2. Create the Chain
qa_chain = qa_prompt | llm | StrOutputParser()

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


        return {
            "answer": answer_text,
            "citations": citations 
        }
    except Exception as e:
        print(f"RAG Error: {e}")
        return {"answer": f"Lỗi AI: {str(e)}", "citations": []}