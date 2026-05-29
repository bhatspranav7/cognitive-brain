from backend.retrieval.adaptive_retriever import adaptive_retrieve

result = adaptive_retrieve(
    "What skills does Pranav have?"
)

print()

print("BOOST LEVEL:")
print(result["boost"])

print()

print("DOCUMENTS:")
print(result["documents"])

print()

print("METADATA:")
print(result["metadatas"])