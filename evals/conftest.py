"""Shared fixtures and helpers for the FlexBot evals.

Split across `test_flexbot.py` (LLMTestCase-based evals) and
`test_flexbot_conversational.py` (ConversationalTestCase-based evals) because
Confident AI rejects a single test run that mixes both test case types.
"""

import os
from dataclasses import dataclass
from typing import Any

import pytest
from deepeval.models import GeminiModel
from deepeval.test_case import ToolCall
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from llm.agent import ChatAgent
from llm.model import build_model
from llm.prompts import CHAT_SYSTEM_PROMPT
from llm.state import CustomAgentState
from llm.tools import get_all_tools, get_hitl_config


@pytest.fixture(scope="module")
def eval_model() -> GeminiModel:
    """Judge model for deepeval metrics -- separate from the agent under test.
    Passed explicitly so deepeval never falls back to its OpenAI default."""
    return GeminiModel(
        model="gemini-3.5-flash",
        api_key=os.environ["GOOGLE_API_KEY"],
        temperature=0,
        cost_per_input_token=1.50 / 1_000_000,
        cost_per_output_token=9 / 1_000_000,
    )


@pytest.fixture
def chat_agent() -> ChatAgent:
    """Fresh agent per test; own checkpointer so state never leaks between tests."""
    return ChatAgent(
        model=build_model(os.environ["GOOGLE_API_KEY"]),
        middleware=[HumanInTheLoopMiddleware(interrupt_on=get_hitl_config())],
        tools=get_all_tools(),
        system_prompt=CHAT_SYSTEM_PROMPT,
        checkpointer=InMemorySaver(),
        state=CustomAgentState,
    )


@dataclass
class ConversationResult:
    answer: str
    tools_called: list[ToolCall]
    interrupted: bool
    interrupt_id: str | None
    action_requests: list[dict[str, Any]]


async def run_turn(chat_agent: ChatAgent, message: str, thread_id: str) -> ConversationResult:
    answer_parts: list[str] = []
    tools_called: list[ToolCall] = []
    interrupted = False
    interrupt_id = None
    action_requests: list[dict[str, Any]] = []

    async for event in chat_agent.stream([HumanMessage(content=message)], thread_id=thread_id):
        if event["type"] == "ai":
            answer_parts.append(event["content"])
        elif event["type"] == "tool":
            tools_called.append(ToolCall(name=event["name"], input_parameters=event["input"] or {}))
        elif event["type"] == "interrupt":
            interrupted = True
            interrupt_id = event["interrupt_id"]
            action_requests = event["action_requests"]

    return ConversationResult(
        answer="".join(answer_parts),
        tools_called=tools_called,
        interrupted=interrupted,
        interrupt_id=interrupt_id,
        action_requests=action_requests,
    )


async def resume_turn(
    chat_agent: ChatAgent,
    thread_id: str,
    interrupt_id: str,
    decisions: list[dict[str, Any]],
) -> list[str]:
    """Resume after a HITL interrupt; returns the raw tool-event contents."""
    tool_call_contents: list[str] = []
    async for event in chat_agent.resume(
        thread_id=thread_id, interrupt_id=interrupt_id, decisions=decisions
    ):
        if event["type"] == "tool":
            tool_call_contents.append(event["content"])
    return tool_call_contents
