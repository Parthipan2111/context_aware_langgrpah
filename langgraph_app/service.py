from api.chat_model import ChatRequest, ChatResponse
from shared.build_chat_response import build_chat_response
from utils.combine_final_response import combine_agent_responses
from utils.session_store import load_session
from graph.build_dynamic_graph import build_graph
from utils.utils import start_or_resume
from shared.init_graph_state import init_new_multi_agent_state
from shared.session_model import PendingAgent, SessionState
from vector_db.chroma_utils import persist_user_messages_to_chroma
from agents.IntentRecognitionAgent.intent_recognition_agent import intent_recognition_node
from agents.ContextEnrichmentAgent.context_enrich_agent import context_enrichment_agent
from agents.CreditScoreAgent.credit_score_agent import credit_score_node
from agents.TransactionHistoryAgent.transaction_history_agent import transaction_history
from agents.RouterAgent.router_node import update_state_with_agents
from agents.DisputePaymentSupport.dispute_payment_support_agent import dispute_payment_support
from agents.AccountInsightAgent.account_insight_agent import account_insight_node
from agents.CardManagementAgent.card_management_node import card_management_node
from utils.session_store import save_session



# def run_langgraph(request: ChatRequest):
#     """
#     Execute the LangGraph pipeline.
#     """
#     user_id = request.user_id
#     input_text = request.text
#     session_id = request.session_id

#     # ---- 0. Load session state ----
#     state = load_session(user_id, session_id)

#     if state:
#         session_obj = SessionState(**state) if isinstance(state, dict) else state
#         session_obj.history.append({"role": "user", "content": input_text})
#         session_obj.input = input_text
#         multi_state = {
#             "session": session_obj,
#             "user_input": input_text,
#             "output": ""
#         }
#         updated_state = start_or_resume(multi_state)


#     if not state:
#         # New MultiAgentState (session + user_input + output)
#         multi_state = init_new_multi_agent_state(user_id, session_id, input_text)
#     else:
#         # Existing: Wrap the restored SessionState in MultiAgentState
#         session_obj = SessionState(**state) if isinstance(state, dict) else state
#         session_obj.history.append({"role": "user", "content": input_text})
#         session_obj.input = input_text
#         multi_state = {
#             "session": session_obj,
#             "user_input": input_text,
#             "output": ""
#         }

#     # ---- 1. Resume incomplete workflow if any ----
#     updated_state = get_incomplete_agent_plan(multi_state)


#     if not incomplete_plan and state:
#         return combine_agent_responses(session_obj)

#     if incomplete_plan:
#         agents_to_run = [{"name": state["active_agent"], "mode": "sequential"}]
#         graph = build_graph(agents_to_run)
#         print(f"Resuming incomplete workflow: {incomplete_plan}")
#         multi_state_output = graph.invoke(multi_state)

#     else:
#         multi_state = init_new_multi_agent_state(user_id, session_id, input_text)
#             # ---- 2. Normal path: enrichment -> intent ----
#         phase1_agents = [
#             {"name": "context_enrichment_agent", "mode": "sequential"},
#             {"name": "intent_agent", "mode": "sequential"}
#         ]
#         phase1_graph = build_graph(phase1_agents)
#         print("Multi_state keys:", multi_state.keys())
#         print("Multi_state type:", type(multi_state))
#         multi_state_output = phase1_graph.invoke(multi_state)

#     # ---- 3. Run downstream agents returned by intent ----
#     agents_to_run = multi_state_output["session"].pending_agents
#     if agents_to_run:
#         phase2_graph = build_graph(agents_to_run)
#         multi_state_output = phase2_graph.invoke(multi_state_output)

#     # Save session
#     session_state = multi_state_output["session"]
#     save_session(session_state.model_dump())

#     # ---- Persist user messages into Chroma ----
#     persist_user_messages_to_chroma(session_state)
#     # ---- Return final output ----
#     if "output" not in multi_state_output:
#         multi_state_output["output"] = combine_agent_responses(session_state)
#     return multi_state_output

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
        multi_state_output_final_phase = graph.invoke(updated_state)

    else:
        # ---- 3. No incomplete flow: Normal new flow ----
        phase1_agents = [
            PendingAgent(name="context_enrichment_agent", mode="sequential"),
            PendingAgent(name="intent_agent", mode="sequential"),
            PendingAgent(name="router_node", mode="sequential")
        ]
        phase1_graph = build_graph(phase1_agents)
        print("Multi_state keys:", updated_state.keys())
        print("Multi_state type:", type(updated_state))
        multi_state_output = phase1_graph.invoke(updated_state)

        # After intent detection, get downstream agents
        agents_to_run = multi_state_output["session"].pending_agents
        if agents_to_run:
            phase2_graph = build_graph(agents_to_run)
            multi_state_output_final_phase = phase2_graph.invoke(multi_state_output)

    # ---- 4. Persist updated session ----
    session_state = multi_state_output_final_phase["session"]
    save_session(session_state.model_dump())

    # ---- 5. Persist user messages into Chroma ----
    persist_user_messages_to_chroma(session_state)

    # ---- 6. Final output ----
    chat_response = build_chat_response(multi_state_output_final_phase)

    return chat_response


# async def run_langgraph_stream(input_text: str, user_id: str):
#     """
#     Streaming version: yields tokens progressively.
#     """
#     stream = app_graph.stream({"input": input_text, "user_id": user_id})
#     for event in stream:
#         if "output" in event:
#             yield event["output"]