from api.chat_model import ChatResponse
from shared.MultiAgentState import MultiAgentState
from shared.session_model import SessionState
from utils.combine_final_response import combine_agent_responses


def build_chat_response(session: SessionState) -> ChatResponse:
    """
    Build ChatResponse from final MultiAgentState.
    """
    # Combine agent results into final response text
    final_response = combine_agent_responses(session)
    reasoning: dict = session.reasoning

    return ChatResponse(
        agent_response=final_response,
        user_id=session.user_id,
        reasoning=reasoning

    )