from backend.agents.graph import graph


print("=" * 60)
print("CortexRAG Memory Test")
print("Type 'exit' to quit")
print("=" * 60)

while True:

    query = input("\nAsk: ")

    if query.lower() == "exit":
        break

    result = graph.invoke(
        {
            "query": query
        }
    )

    print("\nAnswer:")
    print("-" * 60)

    print(
        result["answer"]
    )

    print("\nValid:",
          result["is_valid"])

    print(
        "Score:",
        result.get(
            "similarity_score"
        )
    )