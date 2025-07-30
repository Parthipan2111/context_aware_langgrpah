from api.chat_model import ChatResponse
from shared.MultiAgentState import MultiAgentState
from utils.combine_final_response import combine_agent_responses


def build_chat_response(multi_state_output: MultiAgentState) -> ChatResponse:
    """
    Build ChatResponse from final MultiAgentState.
    """
    session = multi_state_output["session"]

    # Combine agent results into final response text
    final_response = combine_agent_responses(session)

    return ChatResponse(
        agent_response=final_response,
        user_id=session.user_id,
        history=session.history
    )