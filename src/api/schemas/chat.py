"""Schemas for the chat API endpoints."""

from typing import Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """ChatRequest represents a request to the chat API, containing the thread ID and the message to be sent."""

    thread_id: str = Field(min_length=1)
    message: str = Field(min_length=1)


class ChatResponse(BaseModel):
    answer: str


class ToolDecision(BaseModel):
    type: Literal["approve", "reject"]
    message: str | None = None


class ChatResumeRequest(BaseModel):
    """Class representing a request to resume a chat after a tool interrupt."""

    thread_id: str = Field(min_length=1)
    interrupt_id: str = Field(min_length=1)
    decisions: list[ToolDecision] = Field(min_length=1)
