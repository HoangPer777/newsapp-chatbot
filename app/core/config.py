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
    OPENAI_API_KEY: str = Field(default="", description="LLM key")
    OPENAI_API_BASE: str = Field(default="https://api.openai.com/v1")
    LLM_MODEL: str = Field(default="gpt-4o-mini")   # thay bằng model bạn train / OAI compat

    # embeddings
    EMBED_PROVIDER: str = Field(default="hf", description="hf|openai")
    EMBED_MODEL_HF: str = Field(default="intfloat/multilingual-e5-base")
    EMBED_MODEL_OAI: str = Field(default="text-embedding-3-large")
    EMBED_DIM: int = 768

    # retrieval
    RETRIEVER_BACKEND: str = Field(default="faiss", description="faiss|pgvector")
    FAISS_DIR: str = "app/data/vectorstore"
    TOP_K_BM25: int = 20
    TOP_K_VEC: int = 20
    TOP_K_FINAL: int = 8
    HYBRID_ALPHA: float = 0.6   # trọng số vector vs bm25 (0..1)

    # pgvector (nếu dùng)
    PG_DSN: str = "postgresql://postgres:postgres@localhost:5432/newsapp"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
