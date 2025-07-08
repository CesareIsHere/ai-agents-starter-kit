from agents import Agent, Runner
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class AgentRegistry:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentRegistry, cls).__new__(cls)
            cls._instance._agents = {}
            cls._instance._triage_agent = None
        return cls._instance
    
    def register_agent(self, agent: Agent) -> None:
        self._agents[agent.name] = agent
        logger.info(f"Agent {agent.name} registered")
    
    def register_triage(self, agent: Agent) -> None:
        self._triage_agent = agent
        logger.info(f"Triage agent {agent.name} registered")
    
    def get_agent(self, name: str) -> Agent:
        return self._agents.get(name)
    
    def get_triage(self) -> Agent:
        return self._triage_agent
    
    def get_all_agents(self) -> List[Agent]:
        return list(self._agents.values())

registry = AgentRegistry()
