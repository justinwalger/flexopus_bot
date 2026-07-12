"""Module for chat-related API routes."""

import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from api.dependencies import get_chat_service
from api.schemas.chat import ChatRequest, ChatResumeRequest
from application.chat_service import ChatService

router = APIRouter()


@router.post("/chat")
async def stream_chat(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
) -> StreamingResponse:
    """Main endpoint for streaming chat responses. It takes a ChatRequest containing the thread ID and message, and streams back the response from the chat service."""

    async def generate():
        async for chunk in service.answer(
            message=request.message,
            thread_id=request.thread_id,
        ):
            yield f"data: {json.dumps(chunk)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )


@router.post("/chat/resume")
async def resume_chat(
    request: ChatResumeRequest,
    service: ChatService = Depends(get_chat_service),
) -> StreamingResponse:
    """Resumes a chat after a tool interrupt. It takes a ChatResumeRequest containing the thread ID, interrupt ID, and the decision made by the user, and streams back the response from the chat service."""

    async def generate():
        async for chunk in service.resume_tool(
            thread_id=request.thread_id,
            interrupt_id=request.interrupt_id,
            decisions=[decision.model_dump(exclude_none=True) for decision in request.decisions],
        ):
            yield f"data: {json.dumps(chunk)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )
