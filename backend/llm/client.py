"""Provider-agnostic LLM and embedding client.

Local development talks to Ollama. Production talks to any
OpenAI-compatible chat API (Groq by default) and embeds with Chroma's
bundled ONNX MiniLM model, so no GPU, model server, or embedding API key
is needed in the cloud.
"""

import requests

from backend import config


class LLMError(RuntimeError):
    """Raised when the configured LLM/embedding backend fails."""


# ------------------------------------------------------------ generation

def generate_response(prompt: str) -> str:
    if config.LLM_PROVIDER == "groq":
        return _chat_completion(
            config.GROQ_BASE_URL, config.GROQ_API_KEY, config.GROQ_MODEL, prompt
        )
    if config.LLM_PROVIDER == "openai":
        return _chat_completion(
            config.OPENAI_BASE_URL, config.OPENAI_API_KEY, config.OPENAI_MODEL, prompt
        )
    return _ollama_generate(prompt)


def _ollama_generate(prompt: str) -> str:
    try:
        response = requests.post(
            f"{config.OLLAMA_HOST}/api/generate",
            json={
                "model": config.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "keep_alive": config.OLLAMA_KEEP_ALIVE,
            },
            timeout=config.LLM_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        raise LLMError(f"Ollama request failed: {exc}") from exc

    if "error" in data:
        raise LLMError(f"Ollama error: {data['error']}")

    return data.get("response", "").strip()


def _chat_completion(base_url: str, api_key: str, model: str, prompt: str) -> str:
    if not api_key:
        raise LLMError(
            f"LLM_PROVIDER is '{config.LLM_PROVIDER}' but no API key is configured"
        )

    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            },
            timeout=config.LLM_TIMEOUT,
        )
        if not response.ok:
            # Surface the provider's own message — it names the bad model or
            # key, which a bare status code hides.
            raise LLMError(
                f"Chat API {response.status_code} for model '{model}': "
                f"{response.text[:400]}"
            )
        data = response.json()
    except requests.RequestException as exc:
        raise LLMError(f"Chat API request failed: {exc}") from exc

    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError) as exc:
        raise LLMError(f"Unexpected chat API response: {data}") from exc


# ------------------------------------------------------------ embeddings

_onnx_embedder = None


def get_embedding(text: str) -> list:
    if config.EMBEDDING_PROVIDER == "local":
        return _local_embedding(text)
    return _ollama_embedding(text)


def _local_embedding(text: str) -> list:
    global _onnx_embedder
    if _onnx_embedder is None:
        from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

        _onnx_embedder = ONNXMiniLM_L6_V2()
    return [float(x) for x in _onnx_embedder([text])[0]]


def _ollama_embedding(text: str) -> list:
    try:
        response = requests.post(
            f"{config.OLLAMA_HOST}/api/embeddings",
            json={
                "model": config.OLLAMA_EMBED_MODEL,
                "prompt": text,
                "keep_alive": config.OLLAMA_KEEP_ALIVE,
            },
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        raise LLMError(f"Ollama embedding request failed: {exc}") from exc

    embedding = data.get("embedding")
    if not embedding:
        raise LLMError(f"Ollama returned no embedding: {data}")
    return embedding


# ----------------------------------------------------------------- health

def list_models() -> dict:
    """Ask the configured provider which models this key may actually use.

    Chat APIs answer 404 (not 401) when the key is valid but the model is
    not available to the account, so this is the quickest way to tell a
    misconfigured model from a bad key.
    """
    if config.LLM_PROVIDER == "ollama":
        try:
            response = requests.get(f"{config.OLLAMA_HOST}/api/tags", timeout=10)
            response.raise_for_status()
            return {
                "provider": "ollama",
                "configured": config.OLLAMA_MODEL,
                "available": [m["name"] for m in response.json().get("models", [])],
            }
        except requests.RequestException as exc:
            return {"provider": "ollama", "error": str(exc)}

    if config.LLM_PROVIDER == "groq":
        base_url, api_key, configured = (
            config.GROQ_BASE_URL,
            config.GROQ_API_KEY,
            config.GROQ_MODEL,
        )
    else:
        base_url, api_key, configured = (
            config.OPENAI_BASE_URL,
            config.OPENAI_API_KEY,
            config.OPENAI_MODEL,
        )

    if not api_key:
        return {"provider": config.LLM_PROVIDER, "error": "no API key configured"}

    try:
        response = requests.get(
            f"{base_url}/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=15,
        )
    except requests.RequestException as exc:
        return {"provider": config.LLM_PROVIDER, "error": str(exc)}

    if not response.ok:
        return {
            "provider": config.LLM_PROVIDER,
            "configured": configured,
            "error": f"{response.status_code}: {response.text[:300]}",
        }

    models = sorted(m.get("id", "") for m in response.json().get("data", []))

    return {
        "provider": config.LLM_PROVIDER,
        "configured": configured,
        "configured_is_available": configured in models,
        "available": models,
    }


def llm_available() -> bool:
    """Cheap reachability check used by /health (never spends tokens)."""
    if config.LLM_PROVIDER == "groq":
        return bool(config.GROQ_API_KEY)
    if config.LLM_PROVIDER == "openai":
        return bool(config.OPENAI_API_KEY)
    try:
        return requests.get(f"{config.OLLAMA_HOST}/api/tags", timeout=3).ok
    except requests.RequestException:
        return False
