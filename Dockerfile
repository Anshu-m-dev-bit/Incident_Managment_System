# ---------- Stage 1: Builder ----------
    FROM python:3.10-slim AS builder

    WORKDIR /app
    
    # Install build dependencies
    RUN apt-get update && apt-get install -y gcc build-essential
    
    COPY requirements.txt .
    
    # Install dependencies into a separate directory
    RUN pip install --no-cache-dir --prefix=/install -r requirements.txt
    
    
    # ---------- Stage 2: Final Runtime Image ----------
    FROM python:3.10-slim
    
    WORKDIR /app
    
    # Copy installed dependencies from builder
    COPY --from=builder /install /usr/local
    
    # Copy application code
    COPY . .
    
    EXPOSE 8000
    
    CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]