import time

from backend.memory.vector_store import query_documents
from backend.observability.tracer import trace_agent


def retriever_agent(state):
    start = time.time()

    query = state["query"]

    results = query_documents(query)

    output = {
        "retrieved_docs": results["documents"]
    }

    latency = time.time() - start

    trace_agent(
        agent_name="retriever",
        input_data=query,
        output_data=output,
        latency=latency
    )

    return output