import time

from backend.utils.llm import generate_response
from backend.observability.tracer import trace_agent


def reasoner_agent(state):
    start = time.time()

    query = state["query"]
    docs = state["retrieved_docs"]

    context = "\n\n".join(docs)

    prompt = f"""
You are an intelligent AI assistant.

Use ONLY the context below to answer.

Context:
{context}

Question:
{query}

Answer:
"""

    answer = generate_response(prompt)

    output = {
        "answer": answer
    }

    latency = time.time() - start

    trace_agent(
        agent_name="reasoner",
        input_data=query,
        output_data=output,
        latency=latency
    )

    return output