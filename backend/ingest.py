from backend.memory.vector_store import add_document


def ingest_data():
    documents = [
        "FastAPI is a modern web framework for building APIs with Python.",
        "Ollama allows running large language models locally on your machine.",
        "ChromaDB is a vector database used for storing embeddings.",
        "RAG stands for Retrieval Augmented Generation, combining retrieval with LLMs."
    ]

    for i, doc in enumerate(documents):
        print(f"Adding doc {i}")
        add_document(str(i), doc)

    print("✅ Data ingested successfully!")


if __name__ == "__main__":
    ingest_data()