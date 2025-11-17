"""Tests for the assistant agent.

Uses `TestModel` to verify tool selection without making real API calls.
`TestModel` generates synthetic data based on tool schemas and returns a JSON
summary of tool calls made (which are all that are connected).
"""

import pytest
from pydantic_ai import models
from pydantic_ai.models.test import TestModel

from nestor.agents.assistant import agent

models.ALLOW_MODEL_REQUESTS = False


@pytest.fixture
def test_agent():
    """Agent with TestModel."""
    with agent.override(model=TestModel()):
        yield agent


def test_assistant_calls_datetime_tools(test_agent):
    """Should call date/time tools for temporal queries."""
    result = test_agent.run_sync("What time is it?")

    assert "get_current_date" in result.output
    assert "get_current_time" in result.output


def test_assistant_calls_web_search_tool(test_agent):
    """Should call web_search for information queries."""
    result = test_agent.run_sync("Latest Python news")

    assert "web_search" in result.output
