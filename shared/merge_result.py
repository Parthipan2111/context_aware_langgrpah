
def safe_merge_agent_result(state, agent_name: str, result: dict) -> dict:
    current = dict(state.get("agent_results", {}))
    current[agent_name] = result
    return {"agent_results": current}