"""Example: application-layer test using a fake ChatAgent, no LLM/LangGraph involved."""

import pytest
from langchain_core.messages import HumanMessage

from application.chat_service import ChatService


class FakeChatAgent:
    def __init__(self):
        self.calls = []

    async def stream(self, messages, thread_id):
        self.calls.append((messages, thread_id))
        for chunk in [{"type": "ai", "content": "hi"}, {"type": "ai", "content": " there"}]:
            yield chunk


@pytest.mark.asyncio
async def test_answer_strips_message_and_forwards_chunks():
    fake_agent = FakeChatAgent()
    service = ChatService(agent=fake_agent)

    chunks = [chunk async for chunk in service.answer(message="  hello  ", thread_id="t1")]

    assert chunks == [{"type": "ai", "content": "hi"}, {"type": "ai", "content": " there"}]
    [(messages, thread_id)] = fake_agent.calls
    assert thread_id == "t1"
    assert messages == [HumanMessage(content="hello")]


@pytest.mark.asyncio
async def test_answer_rejects_empty_message():
    service = ChatService(agent=FakeChatAgent())

    with pytest.raises(ValueError):
        async for _ in service.answer(message="   ", thread_id="t1"):
            pass
