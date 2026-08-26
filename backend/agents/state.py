from typing import TypedDict


class AgentState(TypedDict, total=False):

    query: str

    retrieved_docs: list

    retrieval_metadata: list

    retrieval_boost: str

    distances: list

    answer: str

    is_valid: bool

    similarity_score: float

    retry_count: int
