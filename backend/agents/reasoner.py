from backend.llm.ollama_client import generate_response


def reasoner_agent(state):

    query = state["query"]

    docs = state.get("retrieved_docs", [])

    context = "\n\n".join(docs)

    prompt = f"""
You are a grounded AI assistant.

Answer ONLY using the provided context.

If the answer is not present in the context,
reply with:
"I don't know based on the provided documents."

Context:
{context}

Question:
{query}

Answer:
"""

    answer = generate_response(prompt)

    state["answer"] = answer

    return state