# app/graph_builder.py
from langgraph.graph import StateGraph,START, END
from typing import List, Dict, Any

AGENT_FUNCTIONS = {}

def register_agent(name):
    """Decorator to register an agent function."""
    def wrapper(func):
        AGENT_FUNCTIONS[name] = func
        return func
    return wrapper

def build_graph(agent_plan: List[Dict[str, str]]):
    workflow = StateGraph(dict)
    last_sequential = None

    for agent in agent_plan:
        name, mode = agent.name, agent.mode
        if name not in AGENT_FUNCTIONS:
            raise ValueError(f"Agent {name} not registered.")
        workflow.add_node(name, AGENT_FUNCTIONS[name])

    # Add edges based on the agent plan

    for i, agent in enumerate(agent_plan):
        name, mode = agent.name, agent.mode

        if not last_sequential:
            workflow.add_edge(START, name)  

        if mode == "sequential":
            if last_sequential:
                workflow.add_edge(last_sequential, name)
                last_sequential = name
            else:
                last_sequential = name
        else:  # parallel
            if last_sequential:
                workflow.add_edge(last_sequential, name)

    for agent in agent_plan:
        if agent.name == "parallel":
            workflow.add_edge(agent.name, END)
    if last_sequential:
        workflow.add_edge(last_sequential, END)

    return workflow.compile()
