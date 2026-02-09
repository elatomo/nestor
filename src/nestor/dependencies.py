"""Shared dependencies for Néstor."""

from dataclasses import dataclass

from . import defaults


@dataclass
class AssistantDeps:
    """Dependencies for assistant agent."""

    search_backend: str
    safesearch: defaults.SafeSearchLevel
    default_location: str
