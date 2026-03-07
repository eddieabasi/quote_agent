"""Dockie Quote multi-agent pipeline: Gather, Analyze, Recommend, Export."""

from agents.analyze import analyze_agent
from agents.export_agent import export_agent
from agents.gather import gather_agent
from agents.recommend import recommend_agent

from google.adk.agents import LlmAgent

# Root agent: runs the four sub-agents in order for observability.
dockie_quote_agent = LlmAgent(
    name="DockieQuote",
    sub_agents=[gather_agent, analyze_agent, recommend_agent, export_agent],
)

__all__ = [
    "dockie_quote_agent",
    "gather_agent",
    "analyze_agent",
    "recommend_agent",
    "export_agent",
]
