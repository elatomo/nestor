"""Configuration management for Néstor.

Loads settings from environment variables and .env file.
"""

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", frozen=True)

    # LLM Configuration
    openai_api_key: SecretStr


# Global settings instance
settings = Settings()
