import chromadb
import os

from backend.utils.embeddings import get_embedding

# Base directory
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(__file__)
    )
)

# Persistent DB path
PERSIST_DIR = os.path.join(BASE_DIR, "chroma_db")

# Chroma client
client = chromadb.PersistentClient(path=PERSIST_DIR)

# Collection
collection = client.get_or_create_collection(
    name="cortex_memory"
)


def add_document(doc_id: str, text: str, metadata=None):

    # Clean text
    text = text.strip()

    # Skip empty chunks
    if not text:
        print(f"Skipping empty chunk: {doc_id}")
        return

    # Generate embedding
    embedding = get_embedding(text)

    # DEBUG
    print(f"Embedding length for chunk {doc_id}: {len(embedding)}")

    # Skip invalid embeddings
    if not embedding or len(embedding) == 0:
        print(f"Skipping invalid embedding for chunk: {doc_id}")
        return

    # Store
    collection.add(
        ids=[str(doc_id)],
        documents=[text],
        embeddings=[embedding],
        metadatas=[metadata or {}]
    )

    print(f"Stored chunk: {doc_id}")


def query_documents(query: str, top_k=3):

    embedding = get_embedding(query)

    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k
    )

    return {
        "documents": results["documents"][0],
        "distances": results["distances"][0],
        "metadatas": results["metadatas"][0]
    }