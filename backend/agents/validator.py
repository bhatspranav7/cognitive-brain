import time

from backend.utils.embeddings import get_embedding
from backend.utils.similarity import cosine_similarity
from backend.observability.tracer import trace_agent

SIMILARITY_THRESHOLD = 0.60


def validator_agent(state):
    start = time.time()

    answer = state["answer"]
    docs = state["retrieved_docs"]

    combined_docs = " ".join(docs)

    # Generate embeddings
    answer_embedding = get_embedding(answer)
    docs_embedding = get_embedding(combined_docs)

    # Semantic similarity
    similarity = cosine_similarity(
        answer_embedding,
        docs_embedding
    )

    is_valid = similarity >= SIMILARITY_THRESHOLD

    output = {
        "is_valid": is_valid,
        "similarity_score": round(similarity, 4)
    }

    latency = time.time() - start

    trace_agent(
        agent_name="validator",
        input_data=answer,
        output_data=output,
        latency=latency
    )

    return output