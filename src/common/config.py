"""Centralized environment configuration for the API service.

Shared by `api` and `llm` since both run inside the same container/process
and read the same environment. The Streamlit UI has its own settings module
at `ui/config.py`, since it runs in a separate container with its own env vars.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_provider: str = "google_genai"
    llm_model: str = "gemini-3.1-flash-lite"

    # Fallbacks used only when a request doesn't supply per-session credentials.
    flexopus_api_token: str | None = None
    flexopus_api_url: str | None = None
    google_api_key: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
