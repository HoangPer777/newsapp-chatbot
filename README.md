# NewsApp AI Service

Dịch vụ AI Backend cho ứng dụng đọc báo NewsApp, cung cấp các tính năng thông minh như Tìm kiếm ngữ nghĩa (Semantic Search), Chatbot hỏi đáp (RAG), và Tóm tắt bài báo.

## 🚀 Tính năng chính

1.  **Semantic Search (Tìm kiếm ngữ nghĩa)**:
    *   Cho phép tìm kiếm bài báo dựa trên ý nghĩa câu hỏi thay vì chỉ khớp từ khóa.
    *   Sử dụng **Google Gemini Embeddings** để vector hóa dữ liệu.
    *   Lưu trữ và truy vấn Vector bằng **PostgreSQL + pgvector**.
    *   Trả về kết quả phong phú (Ảnh, Tác giả, Độ phù hợp %).

2.  **RAG Chatbot (Hỏi đáp thông minh)**:
    *   Trả lời câu hỏi của người dùng dựa trên nội dung bài báo cụ thể.
    *   Sử dụng kiến trúc **RAG (Retrieval-Augmented Generation)**.
    *   Tích hợp **LangChain** để quản lý luồng hội thoại và Prompt.
    *   Model: **Gemini 1.5 Flash** (Tốc độ cao, chi phí thấp).

3.  **Summarization (Tóm tắt)**:
    *   Tóm tắt nội dung bài báo dài thành các ý chính ngắn gọn.

4.  **Data Ingestion (Đồng bộ dữ liệu)**:
    *   API để nhận bài viết mới từ Backend chính (Spring Boot), chia nhỏ (chunking), vector hóa và lưu vào DB.

## 🛠 Công nghệ sử dụng

*   **Ngôn ngữ**: Python 3.10+
*   **Framework**: FastAPI
*   **Database**: PostgreSQL (với extension `vector`)
*   **AI/LLM**:
    *   [Google Generative AI (Gemini)](https://ai.google.dev/)
    *   [LangChain](https://www.langchain.com/)
*   **Other Libs**: `psycopg2` (DB Driver), `uvicorn` (Server).

## ⚙️ Cài đặt & Chạy

### 1. Yêu cầu tiên quyết
*   Docker & Docker Compose
*   API Key từ Google AI Studio (Gemini)

### 2. Cấu hình môi trường (.env)
Tạo file `.env` trong thư mục gốc `newsapp-chatbot` (hoặc cấu hình trong `docker-compose.yml`):

```env
# AI Keys
GOOGLE_API_KEY=your_gemini_api_key_here

# Database Config
PG_DSN=postgresql://postgres:postgres@newsapp-pg:5432/newsapp

# Tùy chỉnh Model (Optional)
LLM_MODEL=models/gemini-1.5-flash
EMBED_MODEL_GEMINI=models/text-embedding-004
```

### 3. Khởi chạy với Docker
Dịch vụ được tích hợp trong file `docker-compose.yml` của toàn bộ dự án.

```bash
# Tại thư mục gốc của project (nơi chứa docker-compose.yml chính)
docker compose up -d newsappchatbot
```

### 4. API Endpoints

Document chi tiết có sẵn tại `/docs` (Swagger UI) khi chạy service.

*   `POST /search`: Tìm kiếm bài viết.
    *   Body: `{"query": "..."}`
*   `POST /qa`: Hỏi đáp với bài viết.
    *   Body: `{"question": "...", "articleId": 123}`
*   `POST /summarize`: Tóm tắt văn bản.
*   `POST /ingest`: (Internal) Nhập dữ liệu bài viết mới.

## 📂 Cấu trúc thư mục

```
app/
├── core/           # Config (env vars)
├── routers/        # API Routes (search, qa, ingest...)
├── services/       # Logic xử lý chính
│   ├── llm_client.py   # Kết nối Gemini/LangChain
│   ├── embedder.py     # Tạo Vector Embedding
│   ├── retriever.py    # Truy vấn pgvector (SQL)
│   └── rag_pipeline.py # Luồng xử lý RAG
├── models/         # Pydantic Schemas
└── main.py         # Entry point
```

## 📝 Ghi chú phát triển

*   Cần đảm bảo container `newsapp-pg` (Postgres) đã cài đặt extension `vector`.
*   Khi sửa code Python, cần restart container để áp dụng thay đổi:
    ```bash
    docker compose restart newsappchatbot
    ```
