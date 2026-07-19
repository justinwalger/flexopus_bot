"""Builds the chat model used by ChatAgent, from centralized settings plus an
optional per-request override key."""

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

from common.config import get_settings


def build_model(gemini_api_key: str | None) -> BaseChatModel:
    settings = get_settings()

    return init_chat_model(
        model=settings.llm_model,
        model_provider=settings.llm_provider,
        api_key=gemini_api_key or settings.google_api_key,
    )
