from backend.agents.graph import graph
from backend.memory.feedback_store import save_feedback

query = input("Ask: ")

result = graph.invoke(
    {
        "query": query
    }
)

print("\nAnswer:\n")
print(result["answer"])

rating = int(
    input(
        "\nRate answer (1-5): "
    )
)

save_feedback(
    query,
    result["answer"],
    rating
)

print(
    "\nFeedback saved."
)