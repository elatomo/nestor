"""Néstor's main assistant agent."""

from ..tools.datetime import get_current_date, get_current_time
from ..tools.websearch import web_search
from . import create_agent

INSTRUCTIONS = """You are Néstor, a helpful AI assistant.

Be concise and friendly in your responses."""

agent = create_agent(
    output_type=str,
    instructions=INSTRUCTIONS,
    name="assistant",
)

agent.tool(get_current_date)
agent.tool(get_current_time)
agent.tool(web_search)
