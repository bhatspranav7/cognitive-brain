"""CortexRAG MCP server.

Exposes the running CortexRAG API as MCP tools, so MCP clients like
Claude Desktop / Claude Code can query your documents directly.

Setup:
    pip install "mcp[cli]" requests
    # point at your API (local default shown):
    #   set CORTEX_API_URL=http://127.0.0.1:8000

Register with Claude Code:
    claude mcp add cortexrag -- python -m mcp_server.server

Or in Claude Desktop's config:
    {
      "mcpServers": {
        "cortexrag": {
          "command": "python",
          "args": ["-m", "mcp_server.server"],
          "cwd": "<path-to>/cognitive-brain",
          "env": { "CORTEX_API_URL": "http://127.0.0.1:8000" }
        }
      }
    }
"""

import os

import requests
from mcp.server.fastmcp import FastMCP

API_URL = os.getenv("CORTEX_API_URL", "http://127.0.0.1:8000").rstrip("/")
API_KEY = os.getenv("CORTEX_API_KEY", "")

mcp = FastMCP("cortexrag")


def _headers():
    return {"X-API-Key": API_KEY} if API_KEY else {}


@mcp.tool()
def ask_cortexrag(question: str) -> str:
    """Ask a question against the documents indexed in CortexRAG.
    Returns a grounded answer with confidence score and source citations."""

    response = requests.post(
        f"{API_URL}/query",
        json={"query": question},
        headers=_headers(),
        timeout=600,
    )
    response.raise_for_status()
    data = response.json()

    citations = "\n".join(f"- {c}" for c in data.get("citations", [])) or "- none"

    return (
        f"{data['answer']}\n\n"
        f"Confidence: {data['confidence']:.2f} "
        f"({'grounded' if data['is_valid'] else 'weakly grounded'})\n"
        f"Sources:\n{citations}"
    )


@mcp.tool()
def list_documents() -> str:
    """List the documents currently indexed in CortexRAG's vector store."""

    response = requests.get(f"{API_URL}/documents", timeout=30)
    response.raise_for_status()
    data = response.json()

    if not data["documents"]:
        return "No documents indexed."

    lines = [
        f"- {doc['source']} ({doc['chunks']} chunks)" for doc in data["documents"]
    ]
    lines.append(f"Total chunks: {data['total_chunks']}")
    return "\n".join(lines)


@mcp.tool()
def get_metrics() -> str:
    """Get CortexRAG observability metrics: per-agent latency, answer
    confidence, and user feedback."""

    agents = requests.get(f"{API_URL}/metrics/agents", timeout=30).json()
    confidence = requests.get(f"{API_URL}/metrics/confidence", timeout=30).json()
    feedback = requests.get(f"{API_URL}/metrics/feedback", timeout=30).json()

    lines = ["Agents:"]
    for name, m in agents.items():
        lines.append(
            f"- {name}: {m['count']} runs, avg {m['avg_latency']}s "
            f"(min {m['min_latency']}s / max {m['max_latency']}s)"
        )

    lines.append(
        f"Confidence: avg {confidence['average_confidence']} "
        f"(best {confidence['highest_confidence']})"
    )
    lines.append(
        f"Feedback: {feedback['total_feedback']} ratings, "
        f"avg {feedback['average_rating']}/5"
    )
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
