"""Example: test ChatAgent's event-translation logic in isolation.

ChatAgent.__init__ calls create_agent(...), which needs a real model/checkpointer -
too heavy for a unit test and not what we want to verify here. Instead we bypass
__init__ and inject a fake LangGraph agent that only implements astream_events, so
the test targets the on_tool_start/on_chat_model_stream -> chunk mapping.
"""

import types

import pytest
from langgraph.types import Command

from llm.agent import ChatAgent


class FakeLangGraphAgent:
    def __init__(self, events):
        self._events = events
        self.calls = []

    async def astream_events(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        for event in self._events:
            yield event


def make_chat_agent(events):
    agent = ChatAgent.__new__(ChatAgent)
    agent.agent = FakeLangGraphAgent(events)
    return agent


@pytest.mark.asyncio
async def test_stream_maps_tool_start_event():
    events = [
        {
            "event": "on_tool_start",
            "name": "Gebaude-anzeigen",
            "data": {"input": {}},
        }
    ]
    chat_agent = make_chat_agent(events)

    chunks = [chunk async for chunk in chat_agent.stream([], thread_id="t1")]

    assert chunks == [
        {
            "type": "tool",
            "content": "Tool-Aufruf: Gebaude-anzeigen",
            "name": "Gebaude-anzeigen",
            "input": {},
            "run_id": None,
        }
    ]


@pytest.mark.asyncio
async def test_stream_maps_tool_end_event():
    events = [
        {
            "event": "on_tool_end",
            "name": "Gebaude-anzeigen",
            "data": {"output": types.SimpleNamespace(content="some output")},
        }
    ]
    chat_agent = make_chat_agent(events)

    chunks = [chunk async for chunk in chat_agent.stream([], thread_id="t1")]

    assert chunks == [
        {
            "type": "tool_result",
            "name": "Gebaude-anzeigen",
            "output": "some output",
            "run_id": None,
        }
    ]


@pytest.mark.asyncio
async def test_pause_and_resume_streaming():
    events = [
        {
            "event": "on_tool_start",
            "name": "Gebaude-anzeigen",
            "data": {"input": {}},
        },
        {
            "event": "on_chain_stream",
            "data": {"chunk": {"content": "Tool-Ausgabe"}},
        },
    ]
    chat_agent = make_chat_agent(events)

    chunks = [chunk async for chunk in chat_agent.stream([], thread_id="t1")]

    assert chunks == [
        {
            "type": "tool",
            "content": "Tool-Aufruf: Gebaude-anzeigen",
            "name": "Gebaude-anzeigen",
            "input": {},
            "run_id": None,
        },
    ]


@pytest.mark.asyncio
async def test_stream_yields_interrupt_when_blocked():
    interrupt = types.SimpleNamespace(
        id="interrupt-1",
        value={"action_requests": [{"action": "book_room"}]},
    )
    events = [
        {
            "event": "on_chain_stream",
            "data": {"chunk": {"__interrupt__": [interrupt]}},
        }
    ]
    chat_agent = make_chat_agent(events)

    chunks = [chunk async for chunk in chat_agent.stream([], thread_id="t1")]

    assert chunks == [
        {
            "type": "interrupt",
            "interrupt_id": "interrupt-1",
            "action_requests": [{"action": "book_room"}],
        }
    ]


@pytest.mark.asyncio
async def test_resume_sends_decisions_and_streams_chunks():
    events = [
        {
            "event": "on_tool_start",
            "name": "Raum-buchen",
            "data": {"input": {}},
        },
        {
            "event": "on_chat_model_stream",
            "data": {"chunk": types.SimpleNamespace(content=[{"text": "Erledigt"}])},
        },
    ]
    chat_agent = make_chat_agent(events)
    decisions = [{"type": "accept"}]

    chunks = [
        chunk
        async for chunk in chat_agent.resume(
            thread_id="t1", interrupt_id="interrupt-1", decisions=decisions
        )
    ]

    assert chunks == [
        {"type": "tool", "content": "Tool-Aufruf: Raum-buchen"},
        {"type": "ai", "content": "Erledigt"},
    ]

    [(call_args, call_kwargs)] = chat_agent.agent.calls
    command = call_args[0]
    assert isinstance(command, Command)
    assert command.resume == {"interrupt-1": {"decisions": decisions}}
    assert call_kwargs["config"]["configurable"]["thread_id"] == "t1"
