def validator_agent(state):
    """Lexical grounding check: what fraction of the answer's words appear
    in the retrieved documents. Cheap, deterministic, and good enough to
    catch answers the model invented from thin air."""

    docs = " ".join(state.get("retrieved_docs", [])).lower()
    answer = state.get("answer", "").lower()

    if not docs:
        state["is_valid"] = False
        state["similarity_score"] = 0.0
        return state

    words = answer.split()

    overlap = sum(1 for word in words if word in docs)

    score = overlap / max(len(words), 1)

    state["similarity_score"] = round(score, 4)
    state["is_valid"] = score >= 0.30

    if not state["is_valid"]:
        state["retry_count"] = state.get("retry_count", 0) + 1

    return state
