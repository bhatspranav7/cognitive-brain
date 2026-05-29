from backend.agents.graph import graph


while True:

    query = input(
        "\nAsk a question: "
    )

    if query.lower() == "exit":
        break

    result = graph.invoke({

        "query": query,

        "retry_count": 0
    })

    print()

    print("ANSWER")
    print("=" * 50)

    print(
        result["answer"]
    )

    print()

    print("BOOST LEVEL")
    print("=" * 50)

    print(
        result.get(
            "retrieval_boost",
            "neutral"
        )
    )

    print()

    print("VALID")
    print("=" * 50)

    print(
        result["is_valid"]
    )

    print()

    print("SCORE")
    print("=" * 50)

    print(
        result.get(
            "similarity_score",
            0
        )
    )