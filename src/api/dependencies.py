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


def _describe_booking_create(tool_call, state, runtime) -> str:
    args = tool_call["args"]
    from_time = args.get("from_time", "")
    to_time = args.get("to_time", "")
    bookable_id = args.get("bookable_id")
    location_id = args.get("location_id")
    user_id = args.get("user_id")

    parts = [
        "Buchung anlegen",
        f"von {from_time}" if from_time else None,
        f"bis {to_time}" if to_time else None,
        f"Bookable {bookable_id}" if bookable_id is not None else None,
        f"Location {location_id}" if location_id is not None else None,
        f"User {user_id}" if user_id is not None else None,
    ]

    booking_info = str(args.get("booking_info", "")).strip()
    guest_email = str(args.get("guest_email", "")).strip()
    guest_name = str(args.get("guest_name", "")).strip()

    if booking_info:
        parts.append(f"Info: {booking_info}")
    if guest_name:
        parts.append(f"Gast: {guest_name}")
    if guest_email:
        parts.append(f"E-Mail: {guest_email}")

    return " | ".join(part for part in parts if part)


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
                    "Buchung-anlegen": {
                        "allowed_decisions": ["approve", "reject"],
                        "description": _describe_booking_create,
                    },
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
