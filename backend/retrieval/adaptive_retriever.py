from backend.memory.vector_store import query_documents
from backend.memory.feedback_memory import get_query_score


def adaptive_retrieve(query):

    result = query_documents(query)

    score = get_query_score(query)

    if score is None:

        result["boost"] = "neutral"

        return result

    if score >= 4:

        result["boost"] = "high"

    elif score >= 3:

        result["boost"] = "medium"

    else:

        result["boost"] = "low"

    return result