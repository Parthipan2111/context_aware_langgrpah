from langchain.agents import Tool,ToolMessage
from langchain.schema import ToolMessage
from langchain_groq import ChatGroq
from agents.ContextEnrichmentAgent.context_tools import get_user_metadata, get_session_history
from agents.ContextEnrichmentAgent.prompt import ENRICH_PROMPT_TEMPLATE
from langchain.prompts import PromptTemplate
from agents.ContextEnrichmentAgent.schema import EnrichedResponse
from pydantic import ValidationError
import json

from agents.shared.state import GraphState


llm = ChatGroq(model="llama3-8b-8192", temperature=0.7)


def run_tool_node(state: GraphState) -> dict:    
    """
    Runs the context enrichment node using the provided state.
    This function retrieves user metadata and session history,
    invokes the LLM with the enriched prompt, and returns the enriched context.
    Args:
        state (GraphState): The current state of the graph, containing user input and user ID.  
    Returns:
        dict: A dictionary containing the enriched context and execution trace.
    """
    last =state["messages"][-1]

    tool_calls = last.additional_kwargs["tool_calls"]
    args = json.loads(last.additional_kwargs.get("args", "{}"))

def run_tool_node(state):
    last = state["messages"][-1]
    tool_call = last.additional_kwargs["tool_calls"][0]
    args = json.loads(tool_call["function"]["arguments"])
    name = tool_call["function"]["name"]
    tool_result = name(**args)
    
    state["messages"].append(ToolMessage(
        tool_call_id=tool_call["id"],
        name=tool_call["function"]["name"],
        content=json.dumps(tool_result)
    ))
    return state

def enrich_content(state:GraphState) -> dict:
    metadata = get_user_metadata(state["user_id"])
    sessions = get_session_history(state["user_id"])
    prompt = PromptTemplate.from_template(ENRICH_PROMPT_TEMPLATE)
    chain = prompt | llm
    response = chain.invoke({
        "original_input": state["input"],
        "device": metadata.get("device", ""),
        "location": metadata.get("location", ""),
        "language": metadata.get("language", ""),
        "last_sessions": json.dumps(sessions)
    })
    state["messages"].append({
        "role": "assistant",
        "content": response.content
    })
    enrich_response = parse_enriched_context(response.content)
    print("DEBUG ENRICHED RESPONSE:", enrich_response)
    return enrich_response

def parse_enriched_context(content: dict) -> dict:
        # Parse and validate the response using Pydantic
    try:
        # If response is a string, try to load as JSON
        if isinstance(content, str):
            response_json = json.loads(content)
        else:
            response_json = content
        enriched = EnrichedResponse.model_validate(response_json)
        return enriched.model_dump()
    except (ValidationError, json.JSONDecodeError) as e:
        # Handle invalid response
        return {"error": str(e), "raw_response": content}


    
def context_enrichment_node(state: GraphState) -> GraphState:
    response = enrich_content(state)
    state["context_enrichment_output"] = response
    state["execution_trace"].append(f"🔍 Context enriched: {response}")
    return state
