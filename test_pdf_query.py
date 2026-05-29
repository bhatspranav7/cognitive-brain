from backend.memory.vector_store import query_documents

query = "What projects has Pranav worked on?"

results = query_documents(query)

print("\n=== RETRIEVED RESULTS ===\n")

for i in range(len(results["documents"])):

    print(f"\nResult {i+1}")
    print("-" * 50)

    print("SOURCE:")
    print(results["metadatas"][i])

    print("\nTEXT:")
    print(results["documents"][i][:500])

    print("\nDISTANCE:")
    print(results["distances"][i])