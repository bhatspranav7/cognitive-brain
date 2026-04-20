from memory.vector_store import query_documents
from utils.llm import generate_response


def build_prompt(query: str, docs: list):
    context = "\n\n".join(docs)

    prompt = f"""
You are an intelligent AI assistant.

STRICT RULES:
- Answer ONLY using the provided context
- Do NOT make up information
- If the answer is unclear, say "I don't know"
- Give a clear and complete explanation (2-4 sentences)

Context:
{context}

User Question:
{query}

Helpful Answer:
"""
    return prompt


def rag_query(query: str):
    results = query_documents(query)

    docs = results["documents"][0]

    prompt = build_prompt(query, docs)

    response = generate_response(prompt)

    return response