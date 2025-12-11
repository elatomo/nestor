"""Default configuration values."""

from typing import Literal

SafeSearchLevel = Literal["on", "moderate", "off"]

MODEL = "gpt-4o-mini"
MAX_RETRIES = 2
SEARCH_BACKEND = "auto"
SAFESEARCH: SafeSearchLevel = "moderate"
