"""Module for API dependencies.#

Currently simple dependency injection for the ChatService, but can be expanded
in the future to include other dependencies as needed.
"""

from typing import Any

from langchain.agents.middleware import HumanInTheLoopMiddleware

from application.chat_service import ChatService
from llm.agent import ChatAgent
from llm.model import build_model
from llm.prompts import CHAT_SYSTEM_PROMPT
from llm.state import CustomAgentState
from llm.tools import get_all_tools, get_hitl_config
from llm.tools.integrations.flexopus_client import set_flexopus_credentials


def get_chat_service(
    checkpointer: Any,
    flexopus_api_key: str | None,
    flexopus_url: str | None,
    gemini_api_key: str | None,
) -> ChatService:
    """Build a ChatService for the current request, using the Flexopus and Gemini
    credentials the user supplied at the start of the session instead of server-wide
    environment variables."""
    set_flexopus_credentials(flexopus_api_key, flexopus_url)

    agent = ChatAgent(
        model=build_model(gemini_api_key=gemini_api_key),
        # Add HumanInTheLoopMiddleware to the agent to handle tool interrupts. The
        # interrupt_on config is derived from every tool registered with
        # approval_required=True (see @register_tool in llm.tools), so new tools
        # requiring approval don't need to be wired up here.
        middleware=[
            HumanInTheLoopMiddleware(
                interrupt_on=get_hitl_config(),
            ),
        ],
        # build the tools list by combining Flexopus tools and basic tools
        tools=get_all_tools(),
        system_prompt=CHAT_SYSTEM_PROMPT,
        checkpointer=checkpointer,
        state=CustomAgentState,
    )

    return ChatService(agent=agent)
