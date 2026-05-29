from langgraph.graph import StateGraph, END

from backend.agents.state import AgentState
from backend.agents.retriever import retriever_agent
from backend.agents.reasoner import reasoner_agent
from backend.agents.validator import validator_agent

from backend.memory.conversation_memory import save_interaction


# Build graph
builder = StateGraph(AgentState)

# Nodes
builder.add_node("retriever", retriever_agent)
builder.add_node("reasoner", reasoner_agent)
builder.add_node("validator", validator_agent)


# Validation routing
def validation_router(state):

    # Save successful interaction
    save_interaction(
        state["query"],
        state["answer"]
    )

    if state["is_valid"]:
        return END

    retry_count = state.get(
        "retry_count",
        0
    )

    if retry_count >= 2:
        return END

    state["retry_count"] = (
        retry_count + 1
    )

    return "reasoner"


# Flow
builder.set_entry_point(
    "retriever"
)

builder.add_edge(
    "retriever",
    "reasoner"
)

builder.add_edge(
    "reasoner",
    "validator"
)

builder.add_conditional_edges(
    "validator",
    validation_router
)

# Compile
graph = builder.compile()