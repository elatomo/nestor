"""Agent creation utilities for Néstor."""

from typing import TypeVar, overload

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from ..config import settings

T = TypeVar("T")
D = TypeVar("D")


@overload
def create_agent(
    output_type: type[T],
    *,
    instructions: str,
    model_name: str | None = None,
    deps_type: None = None,
    name: str | None = None,
) -> Agent[None, T]: ...


@overload
def create_agent(
    output_type: type[T],
    *,
    instructions: str,
    model_name: str | None = None,
    deps_type: type[D],
    name: str | None = None,
) -> Agent[D, T]: ...


def create_agent(
    output_type: type[T],
    *,
    instructions: str = "You are Néstor, a helpful AI assistant.",
    model_name: str | None = None,
    deps_type: type[D] | None = None,
    name: str | None = None,
) -> Agent[None, T] | Agent[D, T]:
    """Create a Néstor agent with common configuration.

    Args:
        output_type: Type of the agent's output
        instructions: Agent instructions (role, capabilities, style)
        model_name: Override default OpenAI model from settings
        deps_type: Optional dependency type (None for no dependencies)
        name: Agent name, used for pydantic-ai's internal identification

    Returns:
        Configured agent instance
    """

    model = OpenAIChatModel(
        model_name or settings.default_model,
        provider=OpenAIProvider(api_key=settings.openai_api_key.get_secret_value()),
    )

    if deps_type is None:
        return Agent(
            model=model,
            output_type=output_type,
            instructions=instructions,
            retries=settings.max_retries,
            name=name,
        )
    else:
        return Agent(
            model=model,
            deps_type=deps_type,
            output_type=output_type,
            instructions=instructions,
            retries=settings.max_retries,
            name=name,
        )
