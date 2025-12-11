"""Date and time information tools."""

import logging
from datetime import UTC, datetime
from typing import TypeVar
from zoneinfo import ZoneInfo

from pydantic_ai import RunContext

logger = logging.getLogger(__name__)

D = TypeVar("D")  # Generic dependency type


def get_current_time(ctx: RunContext[D], timezone: str = "UTC") -> str:
    """Get current time in the specified timezone.

    Args:
        ctx: Agent run context
        timezone: IANA timezone name (e.g., 'America/New_York', 'Europe/Madrid')

    Returns:
        Current time formatted as ISO 8601 string
    """
    try:
        tz = ZoneInfo(timezone)
        now = datetime.now(tz)
        return now.isoformat()
    except Exception:
        logger.exception("Error getting time for timezone %s", timezone)
        raise


def get_current_date(ctx: RunContext[D]) -> str:
    """Get current date in ISO format (YYYY-MM-DD).

    Args:
        ctx: Agent run context

    Returns:
        Current date in ISO format
    """
    return datetime.now(UTC).date().isoformat()
