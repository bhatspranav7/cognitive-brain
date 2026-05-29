from backend.memory.user_memory import (
    remember,
    recall
)

remember(
    "name",
    "Pranav"
)

remember(
    "project",
    "CortexRAG"
)

print()

print(
    recall("name")
)

print(
    recall("project")
)