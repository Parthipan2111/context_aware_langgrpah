from typing import TypedDict, List
from langgraph.graph.message import add_messages
from typing import Annotated


class GraphState(TypedDict):
    input: str
    messages:Annotated[list,add_messages]
    intent: str
    execution_trace: List[str]
    results: dict
    retrieved_context: str
    user_id: str
    session_id: str
    context_enrichment_output: dict
    scratchpad_text: str | None