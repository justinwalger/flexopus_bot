"""Centralized environment configuration for the Streamlit UI service."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    backend_api_url: str


@lru_cache
def get_settings() -> Settings:
    return Settings()
