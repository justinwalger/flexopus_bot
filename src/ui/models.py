from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Role(str, Enum):
    """Enum for message roles."""

    human = "human"
    ai = "ai"


class Message(BaseModel):
    """Message structure for Ollama streaming response."""

    role: Role
    content: str


class Query(BaseModel):
    """Query structure for LLM requests."""

    context: list[Message] = []


class RetrieveContextInput(BaseModel):
    """Input model for context retrieval."""

    query: str | dict[str, Any] = Field(description="The search query string.")
