import yaml
from typing import Dict, List, Any, Optional
from agents import Agent
from .tool_loader import ToolLoader
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class AgentFactory:
    """Factory for creating agents from YAML configuration with auto-discovered tools."""
    
    def __init__(self, config_path: str = "config/agents.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.tool_loader = ToolLoader()
        self.agents: Dict[str, Agent] = {}
        self.system_config = self.config.get('system', {})
        
    def _load_config(self) -> Dict[str, Any]:
        """Load YAML configuration file."""
        try:
            config_file = Path(self.config_path)
            if not config_file.exists():
                raise FileNotFoundError(f"Configuration file {self.config_path} not found")
                
            with open(config_file, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                logger.info(f"Loaded configuration from {self.config_path}")
                return config
        except Exception as e:
            logger.error(f"Failed to load config from {self.config_path}: {e}")
            raise
    
    def _discover_tools(self):
        """Discover all available tools using auto-discovery."""
        if self.config.get('tools', {}).get('auto_discover', True):
            logger.info(f"Auto-discovered {len(self.tool_loader.tools)} tools: {list(self.tool_loader.tools.keys())}")
    
    def create_agents(self) -> Dict[str, Agent]:
        """Create all agents from configuration."""
        self._discover_tools()
        
        agents_config = self.config.get('agents', {})
        globals_config = self.config.get('globals', {})
        
        # First pass: create all agents without handoffs
        for agent_id, agent_config in agents_config.items():
            if not agent_config.get('enabled', True):
                logger.info(f"Skipping disabled agent: {agent_id}")
                continue
                
            try:
                agent = self._create_single_agent(agent_id, agent_config, globals_config)
                self.agents[agent_id] = agent
                logger.info(f"Created agent: {agent_id} ({agent_config['name']})")
            except Exception as e:
                logger.error(f"Failed to create agent {agent_id}: {e}")
                raise
        
        # Second pass: configure handoffs after all agents are created
        self._configure_handoffs(agents_config)
        
        return self.agents
    
    def _create_single_agent(self, agent_id: str, config: Dict[str, Any], globals_config: Dict[str, Any]) -> Agent:
        """Create a single agent instance."""
        # Merge global config with agent-specific config
        merged_config = {**globals_config, **config}
        
        # Get tools for this agent
        tool_names = config.get('tools', [])
        tools = self.tool_loader.get_tools_by_names(tool_names)
        
        if tool_names and not tools:
            logger.warning(f"Agent {agent_id} configured with tools {tool_names} but none were found")
        elif tools:
            logger.info(f"Agent {agent_id} configured with {len(tools)} tools: {tool_names}")
        
        # Create the agent
        agent = Agent(
            name=config['name'],
            instructions=config['instructions'],
            tools=tools,
            model=merged_config.get('model', 'gpt-4'),
        )
        
        return agent
    
    def _configure_handoffs(self, agents_config: Dict[str, Any]):
        """Configure handoffs between agents."""
        for agent_id, config in agents_config.items():
            if 'handoffs' in config and agent_id in self.agents:
                handoff_agents = []
                for handoff_id in config['handoffs']:
                    if handoff_id in self.agents:
                        handoff_agents.append(self.agents[handoff_id])
                        logger.debug(f"Configured handoff: {agent_id} -> {handoff_id}")
                    else:
                        logger.warning(f"Handoff target {handoff_id} not found for agent {agent_id}")
                
                # Update agent with handoffs
                if handoff_agents:
                    self.agents[agent_id].handoffs = handoff_agents
                    logger.info(f"Agent {agent_id} configured with {len(handoff_agents)} handoffs")
    
    def get_default_agent(self) -> Optional[Agent]:
        """Get the default agent (usually triage)."""
        for agent_id, config in self.config.get('agents', {}).items():
            if config.get('is_default', False) and agent_id in self.agents:
                return self.agents.get(agent_id)
        return None
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get a specific agent by ID."""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[str]:
        """List all available agent IDs."""
        return list(self.agents.keys())
    
    def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific agent."""
        if agent_id not in self.agents:
            return None
            
        agent_config = self.config.get('agents', {}).get(agent_id, {})
        agent = self.agents[agent_id]
        
        return {
            "id": agent_id,
            "name": agent.name,
            "type": agent_config.get('type', 'unknown'),
            "description": agent_config.get('description', ''),
            "tools": agent_config.get('tools', []),
            "handoffs": agent_config.get('handoffs', []),
            "enabled": agent_config.get('enabled', True),
            "is_default": agent_config.get('is_default', False)
        }
    
    def get_system_config(self) -> Dict[str, Any]:
        """Get system configuration."""
        return self.system_config
    
    def reload_config(self):
        """Reload configuration (for future hot-reload implementations)."""
        logger.info("Reloading configuration...")
        self.config = self._load_config()
        self.agents.clear()
        self.create_agents()
        logger.info("Configuration reloaded successfully")
