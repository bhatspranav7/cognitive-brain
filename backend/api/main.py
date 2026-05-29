from fastapi import FastAPI
from pydantic import BaseModel
import time

from backend.retrieval.rag_pipeline import rag_query
from backend.observability.logger import log_event

app = FastAPI(title="CortexRAG API")


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str
    latency: float
    retrieved_docs: list
    distances: list


@app.get("/")
def root():
    return {"message": "CortexRAG API is running 🚀"}


@app.post("/query", response_model=QueryResponse)
def query_rag(req: QueryRequest):
    start = time.time()

    result = rag_query(req.query)

    latency = time.time() - start

    log_event(f"Query: {req.query}")
    log_event(f"Docs: {result['retrieved_docs']}")
    log_event(f"Distances: {result['distances']}")
    log_event(f"Answer: {result['answer']}")
    log_event(f"Latency: {latency}")

    return {
        "answer": result["answer"],
        "latency": round(latency, 3),
        "retrieved_docs": result["retrieved_docs"],
        "distances": result["distances"]
    }