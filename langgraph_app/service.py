from api.chat_model import ChatRequest, ChatResponse
from shared.MultiAgentState import MultiAgentState
from shared.build_chat_response import build_chat_response
from utils.combine_final_response import combine_agent_responses
from utils.session_store import load_session
from graph.build_dynamic_graph import build_graph
from utils.utils import start_or_resume
from shared.init_graph_state import init_new_multi_agent_state
from shared.session_model import PendingAgent, SessionState
from vector_db.chroma_utils import persist_user_messages_to_chroma
from others.intent_recognition_agent import intent_recognition_node
from agents.IntentRecognitionAgent.intent_agent import intent_agent_node
from agents.ContextEnrichmentAgent.context_enrich_agent import context_enrichment_agent
from agents.CreditScoreAgent.credit_score_agent import credit_score_node
from agents.TransactionHistoryAgent.transaction_history_agent import transaction_history
from agents.RouterAgent.router_node import update_state_with_agents
from agents.DisputePaymentSupport.dispute_payment_support_agent import dispute_payment_support
from agents.AccountInsightAgent.account_insight_agent import account_insight_node
from agents.CardManagementAgent.card_management_node import card_management_node
from agents.CSATAgent.csat_agent import csat_scoring_node
from agents.HumanAgent.human_agent import human_agent_node
from utils.session_store import save_session
from shared.constants import AGENT_NAME_DICT


def run_langgraph(request: ChatRequest)-> ChatResponse:
    """
    Execute the LangGraph pipeline.
    Handles both:
      - Resuming flows (if pending_agents or active_agent exist)
      - Starting new flows
    """
    user_id = request.user_id
    input_text = request.text
    session_id = request.session_id

    # ---- 0. Load session state ----
    loaded_state = load_session(user_id, session_id)

    # Wrap or create SessionState
    if loaded_state:
        session_obj = SessionState(**loaded_state) if isinstance(loaded_state, dict) else loaded_state
    else:
        session_obj = SessionState(
            user_id=user_id,
            session_id=session_id
        )

    # Always update history and latest user input
    session_obj.add_message("user",  input_text)
    session_obj.input = input_text

    # MultiAgentState
    multi_state = {
        "session": session_obj,
        "user_input": input_text,
        "output": ""
    }

    # ---- 1. Decide whether to resume or start new flow ----
    updated_state = start_or_resume(multi_state)
    session = updated_state["session"]

    # ---- 2. Resume incomplete workflow if pending/active agents exist ----
    if session.pending_agents or session.active_agent:
        # Determine which agents to run
        if session.pending_agents:
            agents_to_run = session.pending_agents
            print(f"Resuming pending agents: {agents_to_run}")
        else:
            # No pending_agents but active_agent exists
            agents_to_run = [PendingAgent(name=session.active_agent, mode="sequential")]
            print(f"Resuming active agent: {session.active_agent}")

        graph = build_graph(agents_to_run)
        multi_state_output_inter_phase = graph.invoke(updated_state)

    else:
        # ---- 3. No incomplete flow: Normal new flow ----
        phase1_agents = [
            PendingAgent(name=AGENT_NAME_DICT["CONTEXT_ENRICHMENT"], mode="sequential"),
            PendingAgent(name=AGENT_NAME_DICT["INTENT_AGENT"], mode="sequential"),
            PendingAgent(name=AGENT_NAME_DICT["ROUTER"], mode="sequential")
        ]
        phase1_graph = build_graph(phase1_agents)
        print("Multi_state keys:", updated_state.keys())
        print("Multi_state type:", type(updated_state))
        multi_state_output = phase1_graph.invoke(updated_state)

        # After intent detection, get downstream agents
        agents_to_run = multi_state_output["session"].pending_agents
        if agents_to_run:
            phase2_graph = build_graph(agents_to_run)
            multi_state_output_inter_phase = phase2_graph.invoke(multi_state_output)
        
    csat_session = multi_state_output_inter_phase["session"]
    multi_state_output_final_phase = MultiAgentState()
    if not csat_session.pending_agents and not csat_session.active_agent:
        csat_agents = [
            PendingAgent(name=AGENT_NAME_DICT["CSAT"], mode="sequential")]
        csat_graph = build_graph(csat_agents)
        multi_state_output_final_phase = csat_graph.invoke(multi_state_output_inter_phase)

    if not multi_state_output_final_phase:
        session_state =multi_state_output_inter_phase["session"]
    else:
        session_state =multi_state_output_final_phase["session"]

    # ---- 4. Persist updated session ----
    save_session(session_state.model_dump())    

    # ---- 5. Persist user messages into Chroma ----
    persist_user_messages_to_chroma(session_state)

    # ---- 6. Final output ----
    chat_response = build_chat_response(session_state)

    return chat_response


# async def run_langgraph_stream(input_text: str, user_id: str):
#     """
#     Streaming version: yields tokens progressively.
#     """
#     stream = app_graph.stream({"input": input_text, "user_id": user_id})
#     for event in stream:
#         if "output" in event:
#             yield event["output"]