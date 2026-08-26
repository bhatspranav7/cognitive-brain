import time

from langgraph.graph import StateGraph, END

from backend.agents.state import AgentState
from backend.agents.retriever import retriever_agent
from backend.agents.reasoner import reasoner_agent
from backend.agents.validator import validator_agent
from backend.observability.tracer import trace_agent

MAX_RETRIES = 2


def _traced(name, fn, summarize):
    """Wrap an agent node so every execution lands in agent_traces.jsonl —
    this is what feeds the /metrics endpoints."""

    def wrapper(state):
        start = time.time()
        result = fn(state)
        latency = time.time() - start
        trace_agent(name, state.get("query", ""), summarize(result), latency)
        return result

    return wrapper


def _retriever_summary(state):
    return {
        "documents_found": len(state.get("retrieved_docs", [])),
        "sources": state.get("retrieval_metadata", []),
        "boost": state.get("retrieval_boost", "neutral"),
    }


def _reasoner_summary(state):
    return {"answer": state.get("answer", "")[:300]}


def _validator_summary(state):
    return {
        "similarity_score": state.get("similarity_score", 0.0),
        "is_valid": state.get("is_valid", False),
    }


builder = StateGraph(AgentState)

builder.add_node("retriever", _traced("retriever", retriever_agent, _retriever_summary))
builder.add_node("reasoner", _traced("reasoner", reasoner_agent, _reasoner_summary))
builder.add_node("validator", _traced("validator", validator_agent, _validator_summary))


def validation_router(state):
    # retry_count is incremented by the validator node itself (router
    # mutations don't persist in LangGraph), so this only reads state.
    if state["is_valid"]:
        return END

    if state.get("retry_count", 0) >= MAX_RETRIES:
        return END

    return "reasoner"


builder.set_entry_point("retriever")
builder.add_edge("retriever", "reasoner")
builder.add_edge("reasoner", "validator")
builder.add_conditional_edges("validator", validation_router)

graph = builder.compile()
