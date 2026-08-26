# Alternative to render.yaml's native Python runtime — use this to deploy
# the API on any container host (Render Docker, Railway, Fly.io, Cloud Run).
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY documents ./documents

ENV LLM_PROVIDER=groq \
    EMBEDDING_PROVIDER=local \
    AUTO_INGEST=true \
    PORT=8000

EXPOSE 8000

CMD ["sh", "-c", "uvicorn backend.api.main:app --host 0.0.0.0 --port ${PORT}"]
