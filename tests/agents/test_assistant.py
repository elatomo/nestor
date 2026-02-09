import pytest
from pydantic import SecretStr
from pydantic_ai import models
from pydantic_ai.models.test import TestModel

from nestor.agents.assistant import create_assistant_agent

models.ALLOW_MODEL_REQUESTS = False


@pytest.fixture
def agent():
    """Agent with TestModel."""
    agent = create_assistant_agent(api_key=SecretStr("secret-api-key"))
    with agent.override(model=TestModel()):
        yield agent


class TestAssistant:
    """Tests for the assistant agent.

    Uses `TestModel` to verify tool selection without making real API calls.

    NOTE: `TestModel` generates synthetic data based on tool schemas and
    returns a JSON summary of tool calls made (which are all that are
    connected).
    """

    @pytest.mark.asyncio
    async def test_assistant_calls_datetime_tools(self, agent, deps):
        """Should call date/time tools for temporal queries."""
        result = await agent.run("What time is it?", deps=deps)

        assert "get_current_date" in result.output
        assert "get_current_time" in result.output

    @pytest.mark.asyncio
    async def test_assistant_calls_web_search_tool(self, agent, deps):
        """Should call web_search for information queries."""
        result = await agent.run("Latest Python news", deps=deps)

        assert "web_search" in result.output

    @pytest.mark.asyncio
    async def test_assistant_respects_custom_model(self, deps):
        """Should use specified model name."""
        agent = create_assistant_agent(
            api_key=SecretStr("sk-test"),
            model_name="gpt-4o",
        )

        assert agent.model.model_name == "gpt-4o"
