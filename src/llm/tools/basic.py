from datetime import datetime

from langchain.tools import tool


@tool(name_or_callable="Tag-ausgeben", description="Get current day of the week")
def get_current_day() -> datetime:
    """Get the current day as timestamp"""

    return datetime.now()


def get_all_basic_tools() -> list:
    """Get all tools for the basic agent."""
    return [
        get_current_day,
    ]
