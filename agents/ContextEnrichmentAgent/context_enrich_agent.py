from graph.build_dynamic_graph import register_agent
from shared.MultiAgentState import MultiAgentState
from shared.session_model import SessionState
from vector_db.chroma_utils import query_past_history


@register_agent("context_enrichment_agent")
def context_enrichment_agent(state) -> MultiAgentState:
    """
    Queries Chroma for similar past messages and appends results to history and output.
    """

    session = state["session"]
    query = state["user_input"]

    # 1. Query Chroma for similar past user messages
    try:
        results = query_past_history(
            user_id=session.user_id,
            query=query,
            n=5  # Adjust the number of results as needed
        )
    except Exception as e:
        state["output"] += f"[Context fetch failed: {str(e)}]"
        return state

    # 2. Extract matches (if any)
    similar_contexts = []
    for doc_list in results.get("documents", []):
        for doc in doc_list:
            similar_contexts.append(doc)

    if similar_contexts:
        # Append to agent output
        for ctx in similar_contexts:
            state["similar_context"] += f"- {ctx}\n"

        # Optionally, store as a system-level message in history
        session.history.append(
            {"role": "system", "content": f"Similar contexts: {similar_contexts}"}
        )


    return state
