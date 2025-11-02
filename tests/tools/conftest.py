from unittest.mock import Mock

import pytest
from pydantic_ai import RunContext


@pytest.fixture
def ctx():
    """Mock RunContext."""
    return Mock(spec=RunContext)
