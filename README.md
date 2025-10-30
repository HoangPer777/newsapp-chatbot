## NewsApp Chatbot

Dịch vụ FastAPI cho demo RAG về tin tức với hai khả năng chính:
- Chatbot hỏi đáp (Q&A) dựa trên ngữ cảnh truy xuất.
- Tóm tắt văn bản cho bài viết hoặc nội dung thô.

Repo được cấu hình sẵn cho mục đích demo mà không cần key AI bên ngoài. Tất cả lời gọi AI đã được mock (giả lập), nên dịch vụ có thể khởi động và trả về phản hồi ổn định.

### Tính năng
- Tóm tắt văn bản qua `POST /summarize`
- Hỏi đáp (Q&A) qua `POST /qa` sử dụng truy xuất lai (BM25 + FAISS) với embedding demo
- Kiểm tra sức khỏe dịch vụ `GET /health`
- Tài liệu API tương tác: Swagger UI (`/docs`) và ReDoc (`/redoc`)

### Công nghệ
- FastAPI + Uvicorn
- FAISS + rank-bm25 (hybrid retrieval)
- Docker + Docker Compose

---

## Bắt đầu nhanh

### Yêu cầu
- Cài đặt Docker Desktop (kèm Docker Compose)
- Cài đặt Git

### Clone repository
```bash
git clone https://github.com/HoangPer777/newsapp-chatbot.git
cd newsapp-chatbot
```

### Build và chạy (Docker Compose)
```bash
docker compose build --no-cache
docker compose up -d
```

Dịch vụ sẽ sẵn sàng tại:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

Kiểm tra trạng thái:
```bash
docker compose ps
docker compose logs --tail=100
```

Dừng dịch vụ:
```bash
docker compose down
```

### Endpoints (Demo)
- `GET /health` → { "status": "ok" }
- `POST /summarize` → trả về thông điệp tóm tắt demo
- `POST /qa` → trả về câu trả lời demo với danh sách trích dẫn rỗng

Bạn có thể thử trực tiếp các request mẫu trong Swagger UI.

---

## Cấu trúc dự án
```
app/
  core/           # config, logging
  routers/        # router FastAPI (health, summarize, qa)
  services/       # retriever, rag pipeline, llm client (mock), embedder (mock)
  models/         # pydantic schemas
  main.py         # khởi tạo FastAPI app
Dockerfile
compose.yaml
requirements.txt
```


## Ghi chú
- Port mặc định là 8000 (xem `compose.yaml` và `Dockerfile`).
- Nếu đổi port trong container, đảm bảo `uvicorn --port` và mapping port của Compose trùng khớp.
- Thư mục dữ liệu FAISS/BM25 demo ở `app/data/`; khi triển khai, cân nhắc mount volume hoặc đóng gói dữ liệu vào image.


