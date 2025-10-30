FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Cài gói hệ thống tối thiểu cho faiss & torch (sentence-transformers sẽ auto-pull)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git curl \
    libglib2.0-0 libsm6 libxext6 libxrender-dev libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml* requirements.txt* ./

# Chọn 1 trong 2: pyproject hoặc requirements
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; \
    else pip install --no-cache-dir .; fi

COPY app app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host","0.0.0.0", "--port","8000", "--workers","1"]
