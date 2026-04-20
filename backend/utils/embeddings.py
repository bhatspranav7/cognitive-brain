import requests

OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"

def get_embedding(text: str):
    response = requests.post(
        OLLAMA_EMBED_URL,
        json={
            "model": "nomic-embed-text",
            "prompt": text
        }
    )
    return response.json()["embedding"]