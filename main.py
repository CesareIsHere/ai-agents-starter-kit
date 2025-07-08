#!/usr/bin/env python3
"""
Configuration-based AI Agents System
Main entry point for testing agents loaded from YAML configuration.
"""

import asyncio
import logging
from pathlib import Path
from app.core.agent_factory import AgentFactory
from agents import Runner

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def main():
    """Test agents loaded from YAML configuration."""
    
    # Configuration path
    config_path = Path("config/agents.yaml")
    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        return
    
    try:
        # Create factory and load agents
        logger.info("Loading agents from configuration...")
        factory = AgentFactory(str(config_path))
        agents = factory.create_agents()
        
        logger.info(f"✅ Loaded {len(agents)} agents: {list(agents.keys())}")
        
        # Get default agent (triage)
        default_agent = factory.get_default_agent()
        if not default_agent:
            logger.error("No default agent configured!")
            return
        
        logger.info(f"📋 Default agent: {default_agent.name}")
        
        # Test with various questions
        test_questions = [
            "What is 25 * 47?",
            "Tell me about the Roman Empire",
            "What's happening in the news about AI today?",
            "Solve this equation: 2x + 5 = 15",
            "Who was Julius Caesar?"
        ]
        
        print("\n" + "="*60)
        print("TESTING CONFIGURATION-BASED AGENTS SYSTEM")
        print("="*60)
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n[TEST {i}] Question: {question}")
            print("-" * 50)
            
            try:
                # Execute through triage agent
                result = await Runner.run(default_agent, question)
                
                print(f"✅ Agent used: {result.last_agent.name}")
                print(f"📝 Answer: {result.final_output}")
                
                # Show tools called if available
                if hasattr(result, 'tool_calls') and result.tool_calls:
                    print(f"🔧 Tools used: {[call.function.name for call in result.tool_calls]}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                logger.error(f"Error processing question '{question}': {e}")
        
        print("\n" + "="*60)
        print("CONFIGURATION-BASED AGENTS TEST COMPLETED")
        print("="*60)
        
    except Exception as e:
        logger.error(f"Failed to initialize agents: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())