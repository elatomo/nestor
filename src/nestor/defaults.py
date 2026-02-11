"""Default configuration values."""

from typing import Literal

SafeSearchLevel = Literal["on", "moderate", "off"]

MODEL = "gpt-5-nano"
MAX_RETRIES = 2
SEARCH_BACKEND = "auto"
SAFESEARCH: SafeSearchLevel = "moderate"
DEFAULT_LOCATION = "Madrid"
