from datetime import UTC, datetime
from unittest.mock import patch

import pytest

from nestor.tools.datetime import get_current_date, get_current_time


@pytest.fixture
def now():
    """Mock datetime.now for time-based testing."""
    with patch("nestor.tools.datetime.datetime") as mock_datetime:
        yield mock_datetime.now


class TestGetCurrentTime:
    """Tests for get_current_time."""

    def test_default_utc(self, ctx):
        """Should return UTC time by default."""
        result = get_current_time(ctx)

        # Verify it's a valid ISO 8601 string
        parsed = datetime.fromisoformat(result)
        assert parsed.tzinfo is not None

    def test_custom_timezone(self, ctx):
        """Should return time in specified timezone."""
        result = get_current_time(ctx, timezone="America/New_York")

        parsed = datetime.fromisoformat(result)
        assert parsed.tzinfo is not None

    def test_invalid_timezone_raises(self, ctx):
        """Should raise for invalid timezone."""
        with pytest.raises(Exception):
            get_current_time(ctx, timezone="Invalid/Timezone")

    def test_frozen_time(self, ctx, now):
        """Should return consistent time when frozen."""
        now.return_value = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)

        result = get_current_time(ctx)
        assert "2025-01-15T12:00:00" in result


class TestGetCurrentDate:
    """Tests for get_current_date."""

    def test_returns_iso_format(self, ctx):
        """Should return date in YYYY-MM-DD format."""
        result = get_current_date(ctx)

        # Verify format
        assert len(result) == 10
        assert result[4] == "-"
        assert result[7] == "-"

        assert datetime.fromisoformat(result)

    def test_frozen_date(self, ctx, now):
        """Should return consistent date when frozen."""
        now.return_value = datetime(2025, 1, 15, tzinfo=UTC)

        result = get_current_date(ctx)
        assert result == "2025-01-15"
