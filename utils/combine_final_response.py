import json
def combine_agent_responses(session) -> str:
    """
    Combines all agent responses stored in session.agent_results into a single string.
    Each agent_results entry looks like:
      {
        "slots": {...},
        "agent_response": ["response text 1", "response text 2"]
      }
    """
    responses = []
    for agent_name, result in session.agent_results.items():
        agent_res = result
        # Ensure agent_res is a list
        if isinstance(agent_res, list):
            responses.extend(agent_res)
        elif isinstance(agent_res, str):
            responses.append(agent_res)

    return " ".join(responses) if responses else ""