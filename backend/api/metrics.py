import json
import os

from fastapi import APIRouter

from backend import config

router = APIRouter()

TRACE_FILE = str(config.TRACE_FILE)


def _read_traces():
    if not os.path.exists(TRACE_FILE):
        return []

    traces = []

    with open(TRACE_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                traces.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return traces


@router.get("/metrics/agents")
def get_agent_metrics():

    metrics = {}

    for trace in _read_traces():
        agent = trace.get("agent")
        latency = trace.get("latency", 0)

        if not agent:
            continue

        metrics.setdefault(agent, []).append(latency)

    result = {}

    for agent, values in metrics.items():
        result[agent] = {
            "count": len(values),
            "avg_latency": round(sum(values) / len(values), 4),
            "max_latency": round(max(values), 4),
            "min_latency": round(min(values), 4),
        }

    return result


@router.get("/metrics/history")
def get_query_history():

    queries = []

    for trace in _read_traces():
        if trace.get("agent") == "retriever":
            query = trace.get("input", "")
            if query:
                queries.append(query)

    return queries[-20:]


@router.get("/metrics/feedback")
def get_feedback_metrics():

    feedback_file = str(config.FEEDBACK_FILE)

    empty = {
        "total_feedback": 0,
        "average_rating": 0,
        "highest_rating": 0,
        "lowest_rating": 0,
    }

    if not os.path.exists(feedback_file):
        return empty

    with open(feedback_file, "r", encoding="utf-8") as f:
        feedback = json.load(f)

    if len(feedback) == 0:
        return empty

    ratings = [item["rating"] for item in feedback]

    return {
        "total_feedback": len(ratings),
        "average_rating": round(sum(ratings) / len(ratings), 2),
        "highest_rating": max(ratings),
        "lowest_rating": min(ratings),
    }


@router.get("/metrics/confidence")
def get_confidence_metrics():

    scores = []

    for trace in _read_traces():
        if trace.get("agent") != "validator":
            continue

        output = trace.get("output") or {}

        if isinstance(output, dict):
            score = output.get("similarity_score")
            if score is not None:
                scores.append(score)

    if len(scores) == 0:
        return {
            "average_confidence": 0,
            "highest_confidence": 0,
            "lowest_confidence": 0,
        }

    return {
        "average_confidence": round(sum(scores) / len(scores), 4),
        "highest_confidence": round(max(scores), 4),
        "lowest_confidence": round(min(scores), 4),
    }


@router.get("/metrics/sources")
def get_source_metrics():
    """Which documents actually got retrieved, counted from the traces the
    retriever agent writes (no re-querying of the vector store)."""

    source_counts = {}

    for trace in _read_traces():
        if trace.get("agent") != "retriever":
            continue

        output = trace.get("output") or {}

        if not isinstance(output, dict):
            continue

        for ref in output.get("sources") or []:
            if isinstance(ref, dict):
                source = ref.get("source", "Unknown")
                source_counts[source] = source_counts.get(source, 0) + 1

    return source_counts
