from backend.agents.graph import graph

result = graph.invoke({
    "query": "What is FastAPI?",
    "retry_count": 0
})

print(result)