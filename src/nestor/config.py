"""Configuration management for Néstor.

Loads settings from environment variables and .env file.
"""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from . import defaults


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="nestor_", frozen=True
    )

    # LLM
    openai_api_key: SecretStr
    default_model: str = defaults.MODEL
    max_retries: int = defaults.MAX_RETRIES

    # Search
    search_backend: str = Field(
        default=defaults.SEARCH_BACKEND,
        description="DDGS backend(s): 'auto', 'wikipedia,duckduckgo', etc.",
    )
    safesearch: defaults.SafeSearchLevel = Field(
        default=defaults.SAFESEARCH,
        description="Safe search level: 'on', 'moderate', or 'off'",
    )


# Global settings instance
settings = Settings()
