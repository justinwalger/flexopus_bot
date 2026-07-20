"""Contains all relevant llm tools and agents for the Flexopus application."""

from collections.abc import Callable
from typing import Any

TOOL_REGISTRY = {}


def register_tool(
    key: str,
    approval_required: bool = False,
    hitl_description: str | Callable | None = None,
    allowed_decisions: list[str] | None = None,
):
    """Decorator to register a Flexopus tool in the global registry.

    When `approval_required` is True, the tool is also picked up by
    `get_hitl_config()` and routed through `HumanInTheLoopMiddleware` - no need
    to list the tool separately wherever that middleware is configured.
    """

    def decorator(cls):
        TOOL_REGISTRY[key] = {
            "class": cls,
            "approval_required": approval_required,
            "hitl_description": hitl_description,
            "allowed_decisions": allowed_decisions or ["approve", "reject"],
        }
        return cls

    return decorator


def get_all_tools() -> list:
    """Get all tools for the Flexopus agent."""
    return [entry["class"] for entry in TOOL_REGISTRY.values()]


def get_hitl_config() -> dict[str, Any]:
    """Build the `interrupt_on` config for `HumanInTheLoopMiddleware` from every
    tool registered with `approval_required=True`, keyed by the tool's registered
    name."""
    return {
        entry["class"].name: {
            "allowed_decisions": entry["allowed_decisions"],
            "description": entry["hitl_description"],
        }
        for entry in TOOL_REGISTRY.values()
        if entry["approval_required"]
    }


# Imported for their side effect of registering tools via @register_tool.
# Must come after register_tool is defined above, since these modules import it.
from llm.tools import basic, flexopus  # noqa: E402, F401
