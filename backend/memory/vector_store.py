import chromadb
from utils.embeddings import get_embedding

client = chromadb.Client()
collection = client.get_or_create_collection(name="cortex_memory")

def add_document(doc_id: str, text: str):
    embedding = get_embedding(text)
    collection.add(
        ids=[doc_id],
        documents=[text],
        embeddings=[embedding]
    )

def query_documents(query: str, top_k=3):
    embedding = get_embedding(query)
    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k
    )
    return results