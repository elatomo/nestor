import pytest

from nestor.dependencies import AssistantDeps


@pytest.fixture
def deps():
    """Test dependencies."""
    return AssistantDeps(
        search_backend="auto",
        safesearch="moderate",
        default_location="Madrid",
    )
