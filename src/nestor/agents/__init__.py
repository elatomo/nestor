"""Agent creation utilities for Néstor."""

from types import NoneType
from typing import TypeVar

from pydantic import SecretStr
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from .. import defaults

T = TypeVar("T")
D = TypeVar("D")


def create_agent(
    output_type: type[T],
    *,
    api_key: SecretStr,
    instructions: str = "You are Néstor, a helpful AI assistant.",
    model_name: str = defaults.MODEL,
    max_retries: int = defaults.MAX_RETRIES,
    deps_type: type[D] | None = None,
    name: str | None = None,
) -> Agent[D, T]:
    """Create a Néstor agent with common configuration.

    Args:
        output_type: Type of the agent's output
        api_key: OpenAI API key for authentication
        instructions: Agent instructions (role, capabilities, style)
        model_name: The name of the OpenAI model to use
        max_retries: Maximum number of retries on model failures
        deps_type: Optional dependency type (None for no dependencies)
        name: Agent name, used for pydantic-ai's internal identification

    Returns:
        Configured agent instance
    """

    model = OpenAIChatModel(
        model_name,
        provider=OpenAIProvider(api_key=api_key.get_secret_value()),
    )

    return Agent(
        model=model,
        output_type=output_type,
        instructions=instructions,
        retries=max_retries,
        name=name,
        deps_type=deps_type or NoneType,
    )
