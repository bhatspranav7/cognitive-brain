from typing import TypedDict


class AgentState(TypedDict):

    query: str

    retrieved_docs: list

    retrieval_metadata: list

    retrieval_boost: str

    answer: str

    is_valid: bool

    similarity_score: float

    retry_count: int