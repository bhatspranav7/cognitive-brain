from fastapi import APIRouter
import json
import os

router = APIRouter()

TRACE_FILE = "agent_traces.jsonl"


@router.get("/metrics/agents")
def get_agent_metrics():

    if not os.path.exists(TRACE_FILE):
        return {}

    traces = []

    with open(TRACE_FILE, "r", encoding="utf-8") as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            traces.append(json.loads(line))

    metrics = {}

    for trace in traces:

        agent = trace.get("agent")
        latency = trace.get("latency", 0)

        if not agent:
            continue

        if agent not in metrics:
            metrics[agent] = []

        metrics[agent].append(latency)

    result = {}

    for agent, values in metrics.items():

        result[agent] = {
            "count": len(values),
            "avg_latency": round(sum(values) / len(values), 4),
            "max_latency": round(max(values), 4),
            "min_latency": round(min(values), 4)
        }

    return result


@router.get("/metrics/history")
def get_query_history():

    if not os.path.exists(TRACE_FILE):
        return []

    queries = []

    with open(TRACE_FILE, "r", encoding="utf-8") as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            trace = json.loads(line)

            if trace.get("agent") == "retriever":

                query = trace.get("input", "")

                queries.append(query)

    return queries[-20:]


@router.get("/metrics/feedback")
def get_feedback_metrics():

    feedback_file = "feedback.json"

    if not os.path.exists(feedback_file):

        return {
            "total_feedback": 0,
            "average_rating": 0,
            "highest_rating": 0,
            "lowest_rating": 0
        }

    with open(feedback_file, "r", encoding="utf-8") as f:

        feedback = json.load(f)

    if len(feedback) == 0:

        return {
            "total_feedback": 0,
            "average_rating": 0,
            "highest_rating": 0,
            "lowest_rating": 0
        }

    ratings = [item["rating"] for item in feedback]

    return {
        "total_feedback": len(ratings),
        "average_rating": round(sum(ratings) / len(ratings), 2),
        "highest_rating": max(ratings),
        "lowest_rating": min(ratings)
    }


@router.get("/metrics/confidence")
def get_confidence_metrics():

    if not os.path.exists(TRACE_FILE):

        return {
            "average_confidence": 0,
            "highest_confidence": 0,
            "lowest_confidence": 0
        }

    scores = []

    with open(TRACE_FILE, "r", encoding="utf-8") as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            trace = json.loads(line)

            if trace.get("agent") != "validator":
                continue

            output = trace.get("output", {})

            score = output.get("similarity_score")

            if score is not None:
                scores.append(score)

    if len(scores) == 0:

        return {
            "average_confidence": 0,
            "highest_confidence": 0,
            "lowest_confidence": 0
        }

    return {
        "average_confidence": round(sum(scores) / len(scores), 4),
        "highest_confidence": round(max(scores), 4),
        "lowest_confidence": round(min(scores), 4)
    }


@router.get("/metrics/sources")
def get_source_metrics():

    from backend.memory.vector_store import query_documents

    queries = get_query_history()

    source_counts = {}

    for query in queries:

        try:

            result = query_documents(query)

            metadatas = result.get(
                "metadatas",
                []
            )

            for meta in metadatas:

                source = meta.get(
                    "source",
                    "Unknown"
                )

                source_counts[source] = (
                    source_counts.get(
                        source,
                        0
                    ) + 1
                )

        except Exception as e:
            print(e)

    return source_counts