from langchain.agents import Tool
from langchain_groq import ChatGroq
from langchain.chat_models import ChatOpenAI
from agents.ContextEnrichmentAgent.context_tools import get_user_metadata, get_session_history
from agents.ContextEnrichmentAgent.prompt import ENRICH_PROMPT_TEMPLATE
from langchain.prompts import PromptTemplate
from agents.ContextEnrichmentAgent.schema import EnrichedResponse
from pydantic import ValidationError
import json

from agents.shared.state import GraphState


llm = ChatGroq(model="llama3-8b-8192", temperature=0.7)



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
