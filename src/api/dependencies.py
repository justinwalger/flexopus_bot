"""Module for API dependencies.#

Currently simple dependency injection for the ChatService, but can be expanded
in the future to include other dependencies as needed.
"""

from typing import Any

from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

from application.chat_service import ChatService
from common.config import get_settings
from common.hitl import BOOKING_CREATE_TOOL, BOOKING_DELETE_TOOL
from llm.agent import ChatAgent
from llm.prompts import CHAT_SYSTEM_PROMPT
from llm.tools.basic import get_all_basic_tools
from llm.tools.flexopus import get_all_tools
from llm.tools.formatting import _describe_booking_create, _describe_booking_delete
from llm.tools.integrations.flexopus_client import set_flexopus_credentials


def build_model(gemini_api_key: str) -> BaseChatModel:
    settings = get_settings()

    return init_chat_model(
        model=settings.llm_model,
        model_provider=settings.llm_provider,
        api_key=gemini_api_key,
    )


def get_chat_service(
    checkpointer: Any,
    flexopus_api_key: str,
    flexopus_url: str,
    gemini_api_key: str,
) -> ChatService:
    """Build a ChatService for the current request, using the Flexopus and Gemini
    credentials the user supplied at the start of the session instead of server-wide
    environment variables."""
    set_flexopus_credentials(flexopus_api_key, flexopus_url)

    agent = ChatAgent(
        model=build_model(gemini_api_key=gemini_api_key),
        # Add HumanInTheLoopMiddleware to the agent to handle tool interrupts
        middleware=[
            HumanInTheLoopMiddleware(
                interrupt_on={
                    BOOKING_CREATE_TOOL: {
                        "allowed_decisions": ["approve", "reject"],
                        "description": _describe_booking_create,
                    },
                    BOOKING_DELETE_TOOL: {
                        "allowed_decisions": ["approve", "reject"],
                        "description": _describe_booking_delete,
                    },
                },
            ),
        ],
        # build the tools list by combining Flexopus tools and basic tools
        tools=get_all_tools() + get_all_basic_tools(),
        system_prompt=CHAT_SYSTEM_PROMPT,
        checkpointer=checkpointer,
    )

    return ChatService(agent=agent)
