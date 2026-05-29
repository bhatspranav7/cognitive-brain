from backend.agents.graph import graph
from backend.utils.citation_builder import build_citations


query = input(
    "Ask: "
)

result = graph.invoke(
    {
        "query": query
    }
)

print("\n")
print("=" * 60)

print("ANSWER")
print("=" * 60)

print(
    result["answer"]
)

print("\n")
print("SOURCES")
print("=" * 60)

citations = build_citations(
    result.get(
        "sources",
        []
    )
)

for citation in citations:
    print("-", citation)

print("\n")
print("CONFIDENCE")
print("=" * 60)

print(
    result.get(
        "similarity_score"
    )
)

print("\n")
print(
    "VALID:",
    result["is_valid"]
)