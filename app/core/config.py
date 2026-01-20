# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # service
    APP_NAME: str = "NewsApp Chatbot"
    DEBUG: bool = True
    CORS_ORIGINS: list[str] = ["*"]
    RATE_LIMIT_QPS: float = 5.0              # req/s per client (slowapi)

    # backend spring
    BACKEND_BASE: str = "http://localhost:8080"

    # llm (OpenAI-compatible)
    GOOGLE_API_KEY: str = Field(default="", description="Gemini API Key")
    OPENAI_API_KEY: str = Field(default="", description="LLM key")
    OPENAI_API_BASE: str = Field(default="https://api.openai.com/v1")
    LLM_MODEL: str = Field(default="models/gemini-flash-latest")   # thay bằng model bạn train / OAI compat
    
    ARTICLE_DETAIL_BASE_URL: str = "http://172.20.10.3:8080/api/articles"  # link chi tiết bài báo (cho nguồn tham khảo)
    JAVA_ACCESS_TOKEN: str = Field(default="", description="Token đăng nhập từ Spring Boot")

    # embeddings
    EMBED_PROVIDER: str = Field(default="gemini", description="hf|openai|gemini")
    EMBED_MODEL_HF: str = Field(default="intfloat/multilingual-e5-base")
    EMBED_MODEL_OAI: str = Field(default="text-embedding-3-large")
    EMBED_MODEL_GEMINI: str = Field(default="models/text-embedding-004")
    EMBED_DIM: int = 768

    # retrieval
    RETRIEVER_BACKEND: str = Field(default="pgvector", description="faiss|pgvector")
    FAISS_DIR: str = "app/data/vectorstore"
    TOP_K_BM25: int = 20
    TOP_K_VEC: int = 20
    TOP_K_FINAL: int = 8
    HYBRID_ALPHA: float = 0.6   # trọng số vector vs bm25 (0..1)
    
    # pgvector 
    # NOTE: In docker-compose pipeline, chatbot sees 'newsapp-pg' or 'db' host, BUT
    # user is running 'uvicorn' locally on host, so localhost:5432 is correct if ports are mapped.
    # If running inside docker, it should be 'postgres://postgres:postgres@db:5432/newsapp'
    PG_DSN: str = Field(default="postgresql://postgres:postgres@localhost:5432/newsapp", description="Postgres connection string")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra='ignore')

settings = Settings()
