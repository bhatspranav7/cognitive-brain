def build_citations(sources):

    if not sources:
        return []

    citations = []

    for source in sources:

        filename = source.get(
            "source",
            "Unknown"
        )

        chunk = source.get(
            "chunk",
            "?"
        )

        citations.append(
            f"{filename} (chunk {chunk})"
        )

    return list(
        dict.fromkeys(citations)
    )