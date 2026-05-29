from backend.agents.graph import graph

query = input(
    "Ask a question: "
)

result = graph.invoke(
    {
        "query": query
    }
)

print("\n")

print("ANSWER")
print("=" * 50)

print(result["answer"])

print("\n")
print("SOURCES")
print("=" * 50)

sources = result.get("sources", [])

if len(sources) == 0:
    print("No sources found")
else:
    for source in sources:
        print(source)

print("\n")

print(
    "VALID:",
    result["is_valid"]
)

print(
    "SCORE:",
    result.get(
        "similarity_score"
    )
)