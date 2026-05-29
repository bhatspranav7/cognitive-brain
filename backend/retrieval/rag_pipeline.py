from backend.memory.vector_store import query_documents
from backend.utils.llm import generate_response


def build_prompt(query: str, docs: list):
    context = "\n\n".join(docs)

    return f"""
You are an AI assistant.

Answer ONLY from the context below.
If not found, say "I don't know".

Context:
{context}

Question:
{query}

Answer:
"""


def rag_query(query: str):
    results = query_documents(query)

    docs = results["documents"]
    distances = results["distances"]

    if not docs:
        return {
            "answer": "I don't know (no data found)",
            "retrieved_docs": [],
            "distances": []
        }

    prompt = build_prompt(query, docs)
    answer = generate_response(prompt)

    return {
        "answer": answer,
        "retrieved_docs": docs,
        "distances": distances
    }