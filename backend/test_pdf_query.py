from backend.memory.vector_store import query_documents

results = query_documents(
    "What projects has Pranav worked on?"
)

print("\n=== RESULTS ===\n")

for i in range(len(results["documents"])):

    print(f"\nResult {i+1}")
    print("-" * 50)

    print("Metadata:")
    print(results["metadatas"][i])

    print("\nText:")
    print(results["documents"][i][:500])

    print("\nDistance:")
    print(results["distances"][i])