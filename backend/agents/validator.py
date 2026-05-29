def validator_agent(state):

    docs = " ".join(
        state.get(
            "retrieved_docs",
            []
        )
    ).lower()

    answer = state.get(
        "answer",
        ""
    ).lower()

    if not docs:

        state["is_valid"] = False
        state["similarity_score"] = 0.0

        return state

    overlap = 0

    for word in answer.split():

        if word in docs:
            overlap += 1

    score = overlap / max(
        len(answer.split()),
        1
    )

    state["similarity_score"] = round(
        score,
        4
    )

    state["is_valid"] = score >= 0.30

    return state