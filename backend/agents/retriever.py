from backend.memory.vector_store import query_documents


def retriever_agent(state):

    query = state["query"]

    results = query_documents(
        query,
        top_k=5
    )

    state["retrieved_docs"] = results.get(
        "documents",
        []
    )

    state["sources"] = results.get(
        "metadatas",
        []
    )

    state["distances"] = results.get(
        "distances",
        []
    )

    return state