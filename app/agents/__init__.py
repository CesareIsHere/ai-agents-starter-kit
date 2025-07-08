from typing import Union
from agents import Agent, CodeInterpreterTool, ComputerTool, FileSearchTool, FunctionTool, HostedMCPTool, ImageGenerationTool, InputGuardrail, GuardrailFunctionOutput, LocalShellTool, Runner, WebSearchTool
from pydantic import BaseModel

from app.tools.get_news_article import get_news_articles
from .registry import registry
import logging

logger = logging.getLogger(__name__)



# Definizione modelli
class HomeworkOutput(BaseModel):
    is_homework: bool
    reasoning: str

# Setup degli agenti
def setup_agents():
    logger.info("Setting up agents...")
    
    # Guardrail agent
    guardrail_agent = Agent(
        name="Guardrail check",
        instructions="Check if the user is asking about homework.",
        output_type=HomeworkOutput,
    )
    
    # Math tutor agent
    math_tutor_agent = Agent(
        name="Math Tutor",
        handoff_description="Specialist agent for math questions",
        instructions="You provide help with math problems. Explain your reasoning at each step and include examples",
    )
    registry.register_agent(math_tutor_agent)
    
    # History tutor agent
    history_tutor_agent = Agent(
        name="History Tutor",
        handoff_description="Specialist agent for historical questions",
        instructions="You provide assistance with historical queries. Explain important events and context clearly.",
    )
    registry.register_agent(history_tutor_agent)

    research_agent = Agent(
        name="Research Agent",
        handoff_description="Specialist agent for research questions",
        instructions="You perform in-depth research on various topics. Use web search and other tools to gather information.",
        tools=[
            get_news_articles,
        ]
    )
    registry.register_agent(research_agent)
    
    # Funzione guardrail
    async def homework_guardrail(ctx, agent, input_data):
        result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
        final_output = result.final_output_as(HomeworkOutput)
        return GuardrailFunctionOutput(
            output_info=final_output,
            tripwire_triggered=not final_output.is_homework,
        )
    
    # Triage agent
    triage_agent = Agent(
        name="Triage Agent",
        instructions="You determine which agent to use based on the user's homework question",
        handoffs=[history_tutor_agent, math_tutor_agent, research_agent],
        
        # Decommentare per attivare il guardrail
        # input_guardrails=[
        #     InputGuardrail(guardrail_function=homework_guardrail),
        # ],
    )
    registry.register_triage(triage_agent)
    
    logger.info("Agents setup complete")
    return triage_agent
