"""Néstor - A personal AI assistant."""

from importlib.metadata import version

from .agents.assistant import create_assistant_agent
from .dependencies import AssistantDeps

__version__ = version("nestor")

__all__ = [
    "create_assistant_agent",
    "AssistantDeps",
]
