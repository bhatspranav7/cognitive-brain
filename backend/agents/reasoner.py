from backend.llm.ollama_client import generate_response
from backend.memory.conversation_memory import get_recent_context


def reasoner_agent(state):

    query = state["query"]

    docs = state.get(
        "retrieved_docs",
        []
    )

    context = "\n\n".join(docs)

    history = get_recent_context()

    memory_context = "\n".join(
        [
            f"Q: {item['question']}\nA: {item['answer']}"
            for item in history
        ]
    )

    prompt = f"""
You are CortexRAG.

Use the previous conversation when relevant.

Use ONLY the provided document context.

If the answer is not present in the documents,
reply:

"I don't know based on the provided documents."

PREVIOUS CONVERSATION:
{memory_context}

DOCUMENT CONTEXT:
{context}

QUESTION:
{query}

ANSWER:
"""

    answer = generate_response(prompt)

    state["answer"] = answer

    return state