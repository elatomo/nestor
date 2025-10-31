"""Configuration management for Néstor.

Loads settings from environment variables and .env file.
"""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", frozen=True)

    # LLM
    openai_api_key: SecretStr
    default_model: str = "gpt-4.1-nano"
    max_retries: int = 2

    # Search
    search_backend: str = Field(
        default="auto",
        description="DDGS backend(s): 'auto', 'wikipedia,duckduckgo', etc.",
    )


# Global settings instance
settings = Settings()
