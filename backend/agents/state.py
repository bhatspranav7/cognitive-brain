from typing import TypedDict, List


class AgentState(TypedDict):
    query: str
    retrieved_docs: List[str]
    answer: str
    is_valid: bool
    similarity_score: float
    retry_count: int