from langchain_openai.chat_models import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_perplexity import ChatPerplexity


from langchain.agents import AgentExecutor, create_openai_functions_agent,Tool
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from agents.shared.state import GraphState
import json
from .schema import EnrichedResponse
from pydantic import ValidationError
from agents.ContextEnrichmentAgent.context_tools import get_user_metadata, get_session_history
from agents.ContextEnrichmentAgent.prompt import ENRICH_PROMPT_TEMPLATE
import re
from vector_db.chroma_utils import save_context_to_vector_db,retrieve_context_from_vector_db

# 1. Define the system message (your custom prompt)
system_message = SystemMessagePromptTemplate.from_template(
ENRICH_PROMPT_TEMPLATE
)

tools = [
    Tool.from_function(name="get_session_history",
                       description="Fetches the user's session history.",
                       func=get_session_history)
]

human_prompt = HumanMessagePromptTemplate.from_template("{user_id}, {original_input}")

# 3. Combine into a chat prompt template
prompt = ChatPromptTemplate.from_messages([system_message, human_prompt,("ai", "{agent_scratchpad}")])

# 4. Load LLM
# llm = ChatOpenAI(model="gpt-4o", temperature=0)

# llm = ChatPerplexity(model="sonar", temperature=0.5)

llm = ChatOpenAI(
    model="mistral",
    base_url="http://localhost:11434/v1",  # Ollama API endpoint
)
# llm = ChatGroq(model="llama3-8b-8192", temperature=0.7)
# 5. Build agent
agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

# 6. Initialize AgentExecutor
account_insight_agent = AgentExecutor(agent=agent, tools=tools, verbose=True)

def parse_enriched_context(content: dict) -> dict:
        # Parse and validate the response using Pydantic
    try:
        # If response is a string, try to load as JSON
        if isinstance(content, str):
            # Step 1: Remove the ```json ... ``` wrapper
            json_str = re.sub(r'^```json\n|\n```$', '', content.strip())
            response_json = json.loads(json_str)
        else:
            response_json = content
        enriched = EnrichedResponse.model_validate(response_json)
        return enriched.model_dump()
    except (ValidationError, json.JSONDecodeError) as e:
        # Handle invalid response
        return {"error": str(e), "raw_response": content}


def context_enrichment_node(state:GraphState) -> GraphState:
    user_id = state["user_id"]
    # response = account_insight_agent.run(user_input)
    # old_context = retrieve_context_from_vector_db(state["input"],state["user_id"])
    response_dict = account_insight_agent.invoke({"user_id": user_id, "original_input": state["input"]})
    final_output = response_dict["output"]
    if "intermediate_steps" in final_output:
        scratchpad_text = "\n".join([str(x) for x in final_output["intermediate_steps"]])
    else:
        scratchpad_text = None
    state["scratchpad_text"] = scratchpad_text
    save_context_to_vector_db(state, source="context_enrichment_agent")
  # Default output key for most agents
    # json_response = parse_enriched_context(final_output)
    state["context_enrichment_output"] = final_output
    state["execution_trace"].append(f"🔍 Context enriched: {final_output}")
    state["messages"].append({
        "role": "assistant",
        "content": final_output
    })
    return state