"""Module for API dependencies.#

Currently simple dependency injection for the ChatService, but can be expanded
in the future to include other dependencies as needed.
"""

import os

from fastapi import Request
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

from application.chat_service import ChatService
from llm.agent import ChatAgent
from llm.prompts import CHAT_SYSTEM_PROMPT
from llm.tools.basic import get_all_basic_tools
from llm.tools.flexopus import get_all_tools


def _describe_booking_delete(tool_call, state, runtime) -> str:
    args = tool_call["args"]
    booking_summary = str(args.get("booking_summary", "")).strip()

    if booking_summary:
        return booking_summary

    return f"Buchung löschen (ID: {args.get('booking_id')})"


def build_model() -> BaseChatModel:
    provider = os.getenv("LLM_PROVIDER", "google_genai")
    model_name = os.getenv("LLM_MODEL", "gemini-3.1-flash-lite")

    return init_chat_model(
        model=f"{model_name}",
        model_provider=provider,
    )


def get_chat_service(request: Request) -> ChatService:
    agent = ChatAgent(
        model=build_model(),
        # Add HumanInTheLoopMiddleware to the agent to handle tool interrupts
        middleware=[
            HumanInTheLoopMiddleware(
                interrupt_on={
                    "Buchung-anlegen": True,
                    "Buchung-loeschen": {
                        "allowed_decisions": ["approve", "reject"],
                        "description": _describe_booking_delete,
                    },
                },
            ),
        ],
        # build the tools list by combining Flexopus tools and basic tools
        tools=get_all_tools() + get_all_basic_tools(),
        system_prompt=CHAT_SYSTEM_PROMPT,
        checkpointer=request.app.state.checkpointer,
    )

    return ChatService(agent=agent)
