import chromadb

from backend import config
from backend.llm.client import get_embedding

# Each embedding provider gets its own collection because their vectors
# have different dimensions (nomic-embed-text = 768, MiniLM = 384) and
# Chroma rejects mixed-dimension queries.
_COLLECTION_BY_PROVIDER = {
    "ollama": "cortex_memory",
    "local": "cortex_memory_minilm",
}

client = chromadb.PersistentClient(path=str(config.CHROMA_DIR))

collection = client.get_or_create_collection(
    name=_COLLECTION_BY_PROVIDER.get(config.EMBEDDING_PROVIDER, "cortex_memory")
)


def add_document(doc_id: str, text: str, metadata=None) -> bool:
    text = text.strip()
    if not text:
        return False

    embedding = get_embedding(text)
    if not embedding:
        return False

    collection.upsert(
        ids=[str(doc_id)],
        documents=[text],
        embeddings=[embedding],
        metadatas=[metadata or {}],
    )
    return True


def query_documents(query: str, top_k: int = 3):
    total = collection.count()
    if total == 0:
        return {"documents": [], "distances": [], "metadatas": []}

    embedding = get_embedding(query)

    results = collection.query(
        query_embeddings=[embedding],
        n_results=min(top_k, total),
    )

    return {
        "documents": results["documents"][0],
        "distances": results["distances"][0],
        "metadatas": results["metadatas"][0],
    }


def count() -> int:
    return collection.count()


def list_sources() -> dict:
    """Return {source_filename: chunk_count} for everything indexed."""
    data = collection.get(include=["metadatas"])

    counts = {}
    for meta in data.get("metadatas") or []:
        source = (meta or {}).get("source", "Unknown")
        counts[source] = counts.get(source, 0) + 1

    return counts


def delete_source(source: str) -> int:
    """Delete every chunk belonging to a source file. Returns chunks removed."""
    existing = collection.get(where={"source": source})
    ids = existing.get("ids") or []
    if ids:
        collection.delete(ids=ids)
    return len(ids)
