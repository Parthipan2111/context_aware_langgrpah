# account_insight_agent.py
from fastapi import FastAPI
from pydantic import BaseModel


from urllib import response
from langchain_openai import ChatOpenAI

from langchain.agents import AgentExecutor, create_openai_functions_agent,Tool
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from account_tools import get_account_summary

from dotenv import load_dotenv

load_dotenv()

from prompt import ACCOUNT_INSIGHT_PROMPT

app = FastAPI(title="Account Insight Agent")

# Input model
class InsightRequest(BaseModel):
    user_id: str
    user_input: str


@app.post("/run")
async def run_agent(request: InsightRequest):
    # --- Here you run your business logic ---
    system_message = SystemMessagePromptTemplate.from_template(
        ACCOUNT_INSIGHT_PROMPT
    )

    tools = [
        Tool.from_function(name="get_account_summary",
                        description="Fetches the user's account summary including balances, credit limits, and usage patterns.",
                        func=get_account_summary)
    ]

    human_prompt = HumanMessagePromptTemplate.from_template("{user_id}")

    # 3. Combine into a chat prompt template
    prompt = ChatPromptTemplate.from_messages([system_message, human_prompt,("ai", "{agent_scratchpad}")])

    # 4. Load LLM
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    # 5. Build agent
    agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

    # 6. Initialize AgentExecutor
    account_insight_agent = AgentExecutor(agent=agent, tools=tools, verbose=True)
    response_dict = account_insight_agent.invoke({"user_id": request.user_id, "user_input": request.user_input })

    return response_dict
