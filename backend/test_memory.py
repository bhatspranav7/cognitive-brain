from memory.vector_store import add_document, query_documents

add_document("1", "FastAPI is a modern web framework for Python")
add_document("2", "Ollama allows running LLMs locally")

results = query_documents("What is FastAPI?")
print(results)