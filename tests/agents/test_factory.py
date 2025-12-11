"""Tests for agent factory functions."""

from pydantic import SecretStr
from pydantic_ai import Agent, models
from pydantic_ai.models.test import TestModel

from nestor import defaults
from nestor.agents import create_agent

models.ALLOW_MODEL_REQUESTS = False


class TestCreateAgent:
    """Tests for create_agent factory."""

    def test_creates_agent_without_deps(self):
        """Should create agent without dependencies."""
        agent = create_agent(output_type=str, api_key=SecretStr("secret-api-key"))

        assert isinstance(agent, Agent)
        assert agent.output_type is str
        assert agent.model.model_name == defaults.MODEL
        assert agent.deps_type is type(None)

    def test_creates_agent_with_deps(self):
        """Should create agent with dependencies."""

        class MyDeps:
            value: int = 42

        agent = create_agent(
            output_type=str,
            api_key=SecretStr("secret-api-key"),
            deps_type=MyDeps,
        )

        assert isinstance(agent, Agent)
        assert agent.deps_type is MyDeps

    def test_custom_model_name(self):
        """Should accept custom model name."""
        agent = create_agent(
            output_type=str,
            api_key=SecretStr("secret-api-key"),
            model_name="gpt-4o-mini",
        )

        assert agent.model.model_name == "gpt-4o-mini"

    def test_custom_agent_name(self):
        """Should accept custom agent name."""
        agent = create_agent(
            output_type=str,
            api_key=SecretStr("secret-api-key"),
            name="test_agent",
        )

        assert agent.name == "test_agent"

    def test_with_test_model(self):
        """Should execute successfully with TestModel."""
        agent = create_agent(output_type=str, api_key=SecretStr("secret-api-key"))

        # Override with test model
        with agent.override(model=TestModel()):
            result = agent.run_sync("Hello")
            assert result.output
