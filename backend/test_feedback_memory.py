from backend.memory.feedback_memory import (
    get_average_rating,
    get_query_score
)

print()

print(
    "Average Rating:",
    get_average_rating()
)

print()

print(
    "Query Score:",
    get_query_score(
        "What skills does Pranav have?"
    )
)