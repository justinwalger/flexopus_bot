"""Schemas for the chat API endpoints."""

from typing import Literal

from pydantic import BaseModel, Field


class SessionCredentials(BaseModel):
    """Credentials the user supplies at the start of a chat session."""

    flexopus_api_key: str = Field(min_length=1)
    flexopus_url: str = Field(min_length=1)
    gemini_api_key: str = Field(min_length=1)


class ChatRequest(SessionCredentials):
    """Represents a request to the chat API, containing the thread ID and the message to send."""

    thread_id: str = Field(min_length=1)
    message: str = Field(min_length=1)


class ChatResponse(BaseModel):
    answer: str


class ToolDecision(BaseModel):
    type: Literal["approve", "reject"]
    message: str | None = None


class ChatResumeRequest(SessionCredentials):
    """Class representing a request to resume a chat after a tool interrupt."""

    thread_id: str = Field(min_length=1)
    interrupt_id: str = Field(min_length=1)
    decisions: list[ToolDecision] = Field(min_length=1)
