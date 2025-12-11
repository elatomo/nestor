"""Néstor's main assistant agent."""

from pydantic import SecretStr
from pydantic_ai import Agent

from .. import defaults
from ..dependencies import AssistantDeps
from ..tools.datetime import get_current_date, get_current_time
from ..tools.websearch import web_search
from . import create_agent

INSTRUCTIONS = """You are Néstor, a helpful AI assistant.

Be concise and friendly in your responses."""


def create_assistant_agent(
    *,
    api_key: SecretStr,
    model_name: str = defaults.MODEL,
    max_retries: int = defaults.MAX_RETRIES,
) -> Agent[AssistantDeps, str]:
    """Create assistant agent with explicit configuration."""
    agent = create_agent(
        output_type=str,
        instructions=INSTRUCTIONS,
        name="assistant",
        api_key=api_key,
        model_name=model_name,
        max_retries=max_retries,
        deps_type=AssistantDeps,
    )

    agent.tool(get_current_date)
    agent.tool(get_current_time)
    agent.tool(web_search)

    return agent
