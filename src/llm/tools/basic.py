from datetime import datetime

from langchain.tools import ToolRuntime, tool
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from llm.tools import register_tool


@register_tool("Tag-ausgeben")
@tool(name_or_callable="Tag-ausgeben", description="Get current day of the week")
def get_current_day() -> datetime:
    """Get the current day as timestamp"""

    return datetime.now()


@register_tool("save_user_name")
@tool(
    name_or_callable="Name-speichern",
    description="Saves the user's name for the current conversation.",
)
def save_user_name(name: str, runtime: ToolRuntime) -> Command:
    """Save the user's name to the conversation state."""
    return Command(
        update={
            "name": name,
            "messages": [
                ToolMessage(content="Name gespeichert.", tool_call_id=runtime.tool_call_id)
            ],
        }
    )


@register_tool("save_user_mail")
@tool(
    name_or_callable="Mail-speichern",
    description="Saves the user's email address for the current conversation.",
)
def save_user_mail(mail: str, runtime: ToolRuntime) -> Command:
    """Save the user's email to the conversation state."""
    return Command(
        update={
            "mail": mail,
            "messages": [
                ToolMessage(content="Mail gespeichert.", tool_call_id=runtime.tool_call_id)
            ],
        }
    )
