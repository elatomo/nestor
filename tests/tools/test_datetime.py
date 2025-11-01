from datetime import UTC, datetime
from unittest.mock import Mock, patch

import pytest
from pydantic_ai import RunContext

from nestor.tools.datetime import get_current_date, get_current_time


@pytest.fixture
def mock_ctx():
    """Mock RunContext."""
    return Mock(spec=RunContext)


class TestGetCurrentTime:
    """Tests for get_current_time."""

    def test_default_utc(self, mock_ctx):
        """Should return UTC time by default."""
        result = get_current_time(mock_ctx)

        # Verify it's a valid ISO 8601 string
        parsed = datetime.fromisoformat(result)
        assert parsed.tzinfo is not None

    def test_custom_timezone(self, mock_ctx):
        """Should return time in specified timezone."""
        result = get_current_time(mock_ctx, timezone="America/New_York")

        parsed = datetime.fromisoformat(result)
        assert parsed.tzinfo is not None

    def test_invalid_timezone_raises(self, mock_ctx):
        """Should raise for invalid timezone."""
        with pytest.raises(Exception):
            get_current_time(mock_ctx, timezone="Invalid/Timezone")

    @patch("nestor.tools.datetime.datetime")
    def test_frozen_time(self, mock_datetime, mock_ctx):
        """Should return consistent time when frozen."""
        frozen_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_datetime.now.return_value = frozen_time

        result = get_current_time(mock_ctx)
        assert "2025-01-15T12:00:00" in result


class TestGetCurrentDate:
    """Tests for get_current_date."""

    def test_returns_iso_format(self, mock_ctx):
        """Should return date in YYYY-MM-DD format."""
        result = get_current_date(mock_ctx)

        # Verify format
        assert len(result) == 10
        assert result[4] == "-"
        assert result[7] == "-"

        assert datetime.fromisoformat(result)

    @patch("nestor.tools.datetime.datetime")
    def test_frozen_date(self, mock_datetime, mock_ctx):
        """Should return consistent date when frozen."""
        frozen = datetime(2025, 1, 15, tzinfo=UTC)
        mock_datetime.now.return_value = frozen

        result = get_current_date(mock_ctx)
        assert result == "2025-01-15"
