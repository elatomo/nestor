"""Date and time information tools."""

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from pydantic_ai import RunContext


def get_current_time(ctx: RunContext[None], timezone: str = "UTC") -> str:
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
    except Exception as e:
        return f"Error getting time for timezone '{timezone}': {e}"


def get_current_date(ctx: RunContext[None]) -> str:
    """Get current date in ISO format (YYYY-MM-DD).

    Args:
        ctx: Agent run context

    Returns:
        Current date in ISO format
    """
    return datetime.now(UTC).date().isoformat()
