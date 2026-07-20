"""Tests for the tool registry and the HITL config dynamically derived from it.

Tools requiring approval are marked via `@register_tool(..., approval_required=True,
hitl_description=...)` at the point they're defined (see llm.tools.flexopus). This
verifies get_hitl_config() picks those up automatically, so nothing needs to be
hardcoded wherever HumanInTheLoopMiddleware is configured.
"""

from llm.tools import TOOL_REGISTRY, get_all_tools, get_hitl_config
from llm.tools.flexopus import create_booking, delete_booking
from llm.tools.formatting import _describe_booking_create, _describe_booking_delete


def test_get_all_tools_returns_the_registered_tool_objects():
    tools = get_all_tools()

    assert create_booking in tools
    assert delete_booking in tools
    assert all(hasattr(tool, "name") for tool in tools)


def test_registry_records_approval_metadata_for_approval_required_tools():
    entry = TOOL_REGISTRY["create_booking"]

    assert entry["approval_required"] is True
    assert entry["hitl_description"] is _describe_booking_create
    assert entry["allowed_decisions"] == ["approve", "reject"]


def test_registry_defaults_approval_metadata_for_tools_without_approval():
    entry = TOOL_REGISTRY["get_user_by_email"]

    assert entry["approval_required"] is False
    assert entry["hitl_description"] is None


def test_get_hitl_config_only_includes_approval_required_tools():
    config = get_hitl_config()

    assert set(config) == {create_booking.name, delete_booking.name}


def test_get_hitl_config_wires_up_the_registered_description_callable():
    config = get_hitl_config()

    assert config[create_booking.name] == {
        "allowed_decisions": ["approve", "reject"],
        "description": _describe_booking_create,
    }
    assert config[delete_booking.name] == {
        "allowed_decisions": ["approve", "reject"],
        "description": _describe_booking_delete,
    }
