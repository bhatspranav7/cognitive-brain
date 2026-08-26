import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, File, Header, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from backend import config
from backend.agents.graph import graph
from backend.api.metrics import router as metrics_router
from backend.ingest_pdf import ingest_file
from backend.llm.client import LLMError, llm_available
from backend.memory import vector_store
from backend.memory.conversation_memory import save_interaction
from backend.memory.feedback_memory import get_average_rating
from backend.memory.feedback_store import save_feedback
from backend.memory.user_memory import forget, load_memory, remember
from backend.observability.logger import log_event
from backend.utils.citation_builder import build_citations

APP_VERSION = "2.0.0"


# Set once the startup index is usable. Ingestion runs off the main thread
# so the port binds immediately (cloud hosts fail a deploy that is slow to
# listen), while /query waits here instead of answering from an empty store.
_index_ready = threading.Event()


def _startup_ingest():
    try:
        if vector_store.count() == 0:
            from backend.ingest_pdf import ingest_pdfs

            print("Vector store empty — auto-ingesting documents/ ...")
            ingest_pdfs()
    except Exception as exc:
        print(f"Auto-ingest failed: {exc}")
    finally:
        _index_ready.set()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if config.AUTO_INGEST:
        threading.Thread(target=_startup_ingest, daemon=True).start()
    else:
        _index_ready.set()
    yield


app = FastAPI(
    title="CortexRAG API",
    description="Cognitive multi-agent RAG system: retriever, reasoner and "
    "validator agents over a Chroma vector store.",
    version=APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(metrics_router)

templates = Jinja2Templates(
    directory=str(config.BASE_DIR / "backend" / "dashboard" / "templates")
)


def require_api_key(x_api_key: str = Header(default="")):
    """No-op unless CORTEX_API_KEY is set (recommended for public deploys)."""
    if config.API_KEY and x_api_key != config.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")


# ------------------------------------------------------------- schemas


class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)


class QueryResponse(BaseModel):
    answer: str
    confidence: float
    is_valid: bool
    boost: str
    retries: int
    latency: float
    citations: list
    sources: list
    retrieved_docs: list
    distances: list


class FeedbackRequest(BaseModel):
    query: str
    answer: str
    rating: int = Field(ge=1, le=5)


class MemoryEntry(BaseModel):
    key: str = Field(min_length=1, max_length=100)
    value: str = Field(max_length=2000)


# --------------------------------------------------------------- routes


@app.get("/")
def root():
    return {"message": "CortexRAG API is running 🚀", "version": APP_VERSION}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": APP_VERSION,
        "llm_provider": config.LLM_PROVIDER,
        "llm_ok": llm_available(),
        "embedding_provider": config.EMBEDDING_PROVIDER,
        "documents_indexed": vector_store.count(),
        "index_ready": _index_ready.is_set(),
    }


@app.get("/dashboard")
def dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html")


@app.post("/query", response_model=QueryResponse, dependencies=[Depends(require_api_key)])
def query_rag(req: QueryRequest):
    """Run the full multi-agent pipeline: retriever -> reasoner ->
    validator (with up to 2 retries when grounding is weak)."""

    # First request after a cold start can arrive while documents/ is still
    # being indexed; wait rather than answer "I don't know" from an empty store.
    _index_ready.wait(timeout=config.INDEX_WAIT_SECONDS)

    start = time.time()

    try:
        result = graph.invoke({"query": req.query, "retry_count": 0})
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    latency = time.time() - start

    answer = result.get("answer", "")
    metadatas = result.get("retrieval_metadata", []) or []

    save_interaction(req.query, answer)

    log_event(f"Query: {req.query}")
    log_event(f"Answer: {answer[:200]}")
    log_event(f"Latency: {round(latency, 3)}")

    return {
        "answer": answer,
        "confidence": result.get("similarity_score", 0.0),
        "is_valid": result.get("is_valid", False),
        "boost": result.get("retrieval_boost", "neutral"),
        "retries": result.get("retry_count", 0),
        "latency": round(latency, 3),
        "citations": build_citations(metadatas),
        "sources": metadatas,
        "retrieved_docs": result.get("retrieved_docs", []),
        "distances": result.get("distances", []),
    }


@app.post("/feedback", dependencies=[Depends(require_api_key)])
def submit_feedback(req: FeedbackRequest):
    """Store a 1-5 star rating. Ratings feed the adaptive retriever's
    boost level for repeat queries."""

    save_feedback(req.query, req.answer, req.rating)

    return {"ok": True, "average_rating": get_average_rating()}


# ------------------------------------------------------------ documents


@app.get("/documents")
def list_documents():
    sources = vector_store.list_sources()

    return {
        "documents": [
            {"source": source, "chunks": chunks}
            for source, chunks in sorted(sources.items())
        ],
        "total_chunks": vector_store.count(),
    }


@app.post("/documents/upload", dependencies=[Depends(require_api_key)])
async def upload_document(file: UploadFile = File(...)):
    filename = Path(file.filename or "upload").name

    if not filename.lower().endswith((".pdf", ".txt")):
        raise HTTPException(status_code=400, detail="Only .pdf and .txt files are supported")

    data = await file.read()

    if len(data) > config.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(
            status_code=413, detail=f"File larger than {config.MAX_UPLOAD_MB} MB"
        )

    if not data:
        raise HTTPException(status_code=400, detail="Empty file")

    dest = config.DOCS_DIR / filename
    dest.write_bytes(data)

    try:
        chunks_stored = ingest_file(dest, source_name=filename)
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not ingest file: {exc}")

    log_event(f"Ingested upload: {filename} ({chunks_stored} chunks)")

    return {"source": filename, "chunks_added": chunks_stored}


@app.delete("/documents/{source}", dependencies=[Depends(require_api_key)])
def delete_document(source: str):
    source = Path(source).name

    removed = vector_store.delete_source(source)

    file_path = config.DOCS_DIR / source
    if file_path.is_file():
        file_path.unlink()

    if removed == 0:
        raise HTTPException(status_code=404, detail=f"No chunks found for '{source}'")

    return {"source": source, "chunks_removed": removed}


# --------------------------------------------------------------- memory


@app.get("/memory")
def get_memory():
    return load_memory()


@app.post("/memory", dependencies=[Depends(require_api_key)])
def set_memory(entry: MemoryEntry):
    remember(entry.key, entry.value)
    return load_memory()


@app.delete("/memory/{key}", dependencies=[Depends(require_api_key)])
def delete_memory(key: str):
    if not forget(key):
        raise HTTPException(status_code=404, detail=f"No memory named '{key}'")
    return load_memory()
