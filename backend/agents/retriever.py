from backend.retrieval.adaptive_retriever import adaptive_retrieve


def retriever_agent(state):

    query = state["query"]

    result = adaptive_retrieve(
        query
    )

    state["retrieved_docs"] = result[
        "documents"
    ]

    state["retrieval_metadata"] = result.get(
        "metadatas",
        []
    )

    state["retrieval_boost"] = result.get(
        "boost",
        "neutral"
    )

    return state