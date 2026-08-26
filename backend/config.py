"""Central configuration for CortexRAG.

Every setting comes from an environment variable (optionally loaded from a
.env file at the repo root), so the same code runs locally against Ollama
and in the cloud against Groq/OpenAI-compatible APIs.
"""

import os
from pathlib import Path

# Silence chromadb's posthog telemetry (broken with newer posthog versions)
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

BASE_DIR = Path(__file__).resolve().parent.parent

try:
    from dotenv import load_dotenv

    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass


def _csv(name: str, default: str) -> list:
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


def _flag(name: str, default: str) -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "on")


def _normalize_ollama_host(raw: str) -> str:
    """Accept the same values the official Ollama tooling does: '0.0.0.0',
    'localhost:11434', 'http://host:port', ... ('0.0.0.0' is a server bind
    address people often set machine-wide; as a client we call loopback)."""
    raw = (raw or "").strip().rstrip("/")
    if not raw:
        return "http://127.0.0.1:11434"

    had_scheme = "://" in raw
    if not had_scheme:
        raw = "http://" + raw

    scheme, rest = raw.split("://", 1)
    host, _, port = rest.partition(":")

    if host in ("0.0.0.0", "localhost"):
        host = "127.0.0.1"
    if not port and (not had_scheme or scheme == "http"):
        port = "11434"

    return f"{scheme}://{host}:{port}" if port else f"{scheme}://{host}"


# ---------------------------------------------------------------- LLM
# LLM_PROVIDER: "ollama" (local), "groq" (cloud, free tier), or "openai"
# (any OpenAI-compatible endpoint, e.g. OpenRouter / OpenAI itself).
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()

OLLAMA_HOST = _normalize_ollama_host(os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434"))

# Generation timeout. Local CPU inference can spend minutes just loading
# the model, so keep this generous; cloud providers answer in seconds.
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT_SECONDS", "600"))

# How long Ollama keeps the model in RAM after a request ("30m", "1h", ...)
# so only the first query of a session pays the model-load cost.
OLLAMA_KEEP_ALIVE = os.getenv("OLLAMA_KEEP_ALIVE", "30m")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")

# ---------------------------------------------------------- Embeddings
# EMBEDDING_PROVIDER: "ollama" (nomic-embed-text via local Ollama) or
# "local" (Chroma's bundled ONNX MiniLM — runs in-process, no server,
# no API key; this is what production uses).
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "ollama").lower()

# ------------------------------------------------------------- Storage
DATA_DIR = Path(os.getenv("DATA_DIR", str(BASE_DIR)))
CHROMA_DIR = Path(os.getenv("CHROMA_DIR", str(BASE_DIR / "chroma_db")))
DOCS_DIR = Path(os.getenv("DOCS_DIR", str(BASE_DIR / "documents")))

for _dir in (DATA_DIR, CHROMA_DIR, DOCS_DIR):
    _dir.mkdir(parents=True, exist_ok=True)

TRACE_FILE = DATA_DIR / "agent_traces.jsonl"
FEEDBACK_FILE = DATA_DIR / "feedback.json"
USER_MEMORY_FILE = DATA_DIR / "user_memory.json"
LOG_FILE = DATA_DIR / "logs.txt"

# ----------------------------------------------------------------- API
ALLOWED_ORIGINS = _csv("ALLOWED_ORIGINS", "*")

# Optional shared secret. When set, mutating endpoints require the
# X-API-Key header to match. Empty string disables auth (local dev).
API_KEY = os.getenv("CORTEX_API_KEY", "")

# Ingest the PDFs in DOCS_DIR at startup when the vector store is empty.
# This makes a fresh cloud deploy answer questions out of the box.
AUTO_INGEST = _flag("AUTO_INGEST", "true")

MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "25"))

# How long a query waits for the startup ingest to finish before proceeding.
INDEX_WAIT_SECONDS = int(os.getenv("INDEX_WAIT_SECONDS", "180"))
