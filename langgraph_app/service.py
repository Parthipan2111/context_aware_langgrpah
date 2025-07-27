from api.chat_model import ChatRequest
from utils.session_store import load_session
from graph.build_dynamic_graph import build_graph
from utils.utils import get_incomplete_agent_plan
from shared.init_graph_state import init_new_multi_agent_state
from shared.session_model import SessionState
from vector_db.chroma_utils import persist_user_messages_to_chroma
from agents.IntentRecognitionAgent.intent_recognition_agent import intent_recognition_node
from agents.ContextEnrichmentAgent.context_enrich_agent import context_enrichment_agent
from agents.AccountInsightAgent.account_insight_agent import account_insight_node
from agents.CreditScoreAgent.credit_score_agent import credit_score_node
from utils.session_store import save_session



def run_langgraph(request: ChatRequest):
    """
    Execute the LangGraph pipeline.
    """
    user_id = request.user_id
    input_text = request.text
    session_id = request.session_id

    # ---- 0. Load session state ----
    state = load_session(user_id, session_id)

    if not state:
        # New MultiAgentState (session + user_input + output)
        multi_state = init_new_multi_agent_state(user_id, session_id, input_text)
    else:
        # Existing: Wrap the restored SessionState in MultiAgentState
        session_obj = SessionState(**state) if isinstance(state, dict) else state
        session_obj.history.append({"role": "user", "content": input_text})
        session_obj.input = input_text
        multi_state = {
            "session": session_obj,
            "user_input": input_text,
            "output": ""
        }

    # ---- 1. Resume incomplete workflow if any ----
    incomplete_plan = get_incomplete_agent_plan(multi_state)

    if incomplete_plan:
        agents_to_run = [{"name": state["active_agent"], "mode": "sequential"}]
        graph = build_graph(agents_to_run)
        print(f"Resuming incomplete workflow: {incomplete_plan}")
        multi_state_output = graph.invoke(multi_state)

    else:
            # ---- 2. Normal path: enrichment -> intent ----
        phase1_agents = [
            {"name": "context_enrichment_agent", "mode": "sequential"},
            {"name": "intent_agent", "mode": "sequential"}
        ]
        phase1_graph = build_graph(phase1_agents)
        print("Multi_state keys:", multi_state.keys())
        print("Multi_state type:", type(multi_state))
        multi_state_output = phase1_graph.invoke(multi_state)

    # ---- 3. Run downstream agents returned by intent ----
    agents_to_run = multi_state_output.get("pending_agents", [])
    if agents_to_run:
        phase2_graph = build_graph(agents_to_run)
        multi_state_output = phase2_graph.invoke(multi_state_output)

    # Save session
    session_state = multi_state_output["session"]
    save_session(user_id, session_state.model_dump())

    # ---- Persist user messages into Chroma ----
    persist_user_messages_to_chroma(session_state)

    return multi_state_output


async def run_langgraph_stream(input_text: str, user_id: str):
    """
    Streaming version: yields tokens progressively.
    """
    stream = app_graph.stream({"input": input_text, "user_id": user_id})
    for event in stream:
        if "output" in event:
            yield event["output"]