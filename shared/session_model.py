from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class HistoryItem(BaseModel):
    role: str  # "user" | "agent" | "system"
    content: str


class AgentSlots(BaseModel):
    # Flexible key-value pairs per agent
    slots: Dict[str, Optional[str]] = Field(default_factory=dict)


class PendingAgent(BaseModel):
    name: str
    mode: str  # "sequential" | "parallel"


class SessionState(BaseModel):
    session_id: str
    user_id: Optional[str] = None  # Optional user ID for multi-user sessions
    active_agent: Optional[str] = None
    history: List[HistoryItem] = Field(default_factory=list)
    global_slots: Dict[str, Optional[str]] = Field(default_factory=dict)
    agent_state: Dict[str, AgentSlots] = Field(default_factory=dict)

    # Multi-agent planning
    pending_agents: List[PendingAgent] = Field(default_factory=list)
    intent: List[str] = Field(default_factory=list)
    input: Optional[str] = None
    similar_context: Optional[str] = None  # For context enrichment
    agent_results: Optional[dict] = Field(default_factory=dict)  # store structured results
    workflow_complete: bool = False  # Indicates if the workflow is complete

    # ---------- Helper methods ----------

    def add_message(self, role: str, content: str):
        self.history.append(HistoryItem(role=role, content=content))

    def get_agent_slots(self, agent_name: str) -> Dict[str, Optional[str]]:
        return self.agent_state.get(agent_name, AgentSlots()).slots

    def update_agent_slot(self, agent_name: str, slot_name: str, value: Optional[str]):
        if agent_name not in self.agent_state:
            self.agent_state[agent_name] = AgentSlots()
        self.agent_state[agent_name].slots[slot_name] = value

    def add_pending_agent(self, name: str, mode: str):
        self.pending_agents.append(PendingAgent(name=name, mode=mode))
