import csv
from io import StringIO
from typing import Any

from langchain.tools import ToolRuntime, tool
from pydantic import EmailStr

from common.hitl import BOOKING_CREATE_TOOL, BOOKING_DELETE_TOOL
from llm.tools import register_tool
from llm.tools.formatting import _describe_booking_create, _describe_booking_delete
from llm.tools.integrations.flexopus_client import FlexopusClient
from llm.tools.schemas import (
    BookableAvailabilityBookable,
    BookableAvailabilityInput,
    BookableBookingResponse,
    BookableIdInput,
    BookingCreateInput,
    BookingDeleteInput,
    BuildingApiInput,
    FlexopusBooking,
    FlexopusUser,
    FlexopusUserExportRow,
    LocationBookable,
    LocationBookableOccupancy,
    LocationBookingsInput,
    LocationBookingsResponse,
    LocationIdInput,
    LocationOccupancyInput,
    UserEmailInput,
)


def _client(timeout: float = 15.0) -> FlexopusClient:
    return FlexopusClient(timeout=timeout)


def _error_payload(message: str, exception: Exception) -> dict[str, Any]:
    return {"error": message, "details": str(exception)}


# BUILDINGS
@register_tool("list_flexopus_buildings")
@tool(
    name_or_callable="Gebaude-anzeigen",
    description="Lists Flexopus office buildings and their available locations.",
)
async def list_flexopus_buildings() -> list[dict[str, Any]] | dict[str, Any]:
    """List Flexopus office buildings and their available locations.

    Use when the user asks about offices, buildings, addresses, floors, or
    locations.
    """
    try:
        return await _client().get("/buildings")
    except RuntimeError as exception:
        return _error_payload("Flexopus returned an error while fetching buildings.", exception)


@register_tool("get_building_bookings")
@tool(
    args_schema=BuildingApiInput,
    name_or_callable="Buchungen_nach_Gebaeude",
    description="Lists Flexopus booking by building",
)
async def get_building_bookings(
    building_id: int, from_date: str, to_date: str
) -> list[FlexopusBooking] | dict[str, Any]:
    """List Flexopus bookings for a specific building within a date range.

    Use when the user asks which bookings exist for a building, or about a
    building's schedule or occupancy by building ID.
    """
    try:
        params = {"from": from_date, "to": to_date}
        payload = await _client().get(f"/buildings/{building_id}/bookings", params=params)
        return [FlexopusBooking.model_validate(item) for item in payload]
    except RuntimeError as exception:
        return _error_payload(
            "Flexopus returned an error while fetching building bookings.", exception
        )


# GROUPS
@register_tool("list_flexopus_groups")
@tool(name_or_callable="Nutzergruppen-anzeigen", description="Lists Flexopus groups ")
async def list_flexopus_groups() -> list[dict[str, Any]] | dict[str, Any]:
    """List Flexopus user groups.

    Use when the user asks about groups, teams, or user group memberships.
    """
    try:
        return await _client().get("/groups")
    except RuntimeError as exception:
        return _error_payload("Flexopus returned an error while listing groups.", exception)


@register_tool("get_user_by_email")
@tool(
    "Nutzer-nach-E-Mail-suchen",
    args_schema=UserEmailInput,
    description=(
        "Searches Flexopus users by their exact email address. "
        "Use this when the user provides an email address and asks for "
        "their Flexopus user record or user ID."
    ),
)
async def get_user_by_email(
    user_email: EmailStr, runtime: ToolRuntime
) -> list[FlexopusUser] | dict[str, Any]:
    """Return the Flexopus user record(s) for an exact email address."""
    try:
        payload = await _client().get(f"/users/by-email/{user_email}")

        items = payload if isinstance(payload, list) else [payload] if payload else []
        users = [FlexopusUser.model_validate(item) for item in items]

        return users if users else {"message": "No Flexopus user found for the provided email."}
    except RuntimeError as exception:
        return _error_payload("Flexopus returned an error while searching by email.", exception)


@register_tool("list_flexopus_users_export")
@tool(
    name_or_callable="Nutzer-export-anzeigen",
    description=(
        "Exports all Flexopus users as CSV from /users/export?format=csv. "
        "Use this when the user asks for all users or a complete user list."
    ),
)
async def list_flexopus_users_export(
    runtime: ToolRuntime,
) -> list[FlexopusUserExportRow] | dict[str, Any]:
    """Return the full Flexopus user export as structured CSV rows."""
    try:
        response_text = await _client(timeout=30.0).get(
            "/users/export",
            params={"format": "csv"},
        )

        if not isinstance(response_text, str):
            response_text = str(response_text)

        reader = csv.DictReader(StringIO(response_text))
        users: list[FlexopusUserExportRow] = []
        user_email = runtime.state.get("mail")

        for user in reader:
            normalized_row = {
                "name": user.get("name", ""),
                "email": user.get("email", ""),
                "department": user.get("department", ""),
                "function": user.get("function", ""),
                "about": user.get("about", ""),
                "notify": user.get("notify", ""),
                "groups": user.get("groups", ""),
                "roles": user.get("roles", ""),
                "timezone": user.get("timezone", ""),
                "id": user.get("id", ""),
                "created": user.get("created", ""),
                "license_plates": user.get("license_plates", ""),
                "phone": user.get("phone", ""),
                "tags": user.get("tags", ""),
                "cost_center": user.get("cost_center", ""),
            }
            users.append(FlexopusUserExportRow.model_validate(normalized_row))

        current_user = [user for user in users if user.email.lower() == user_email]

        return (
            current_user
            if current_user
            else {"message": f"User export is empty or no user found for  ({user_email})."}
        )
    except RuntimeError as exception:
        return _error_payload("Flexopus returned an error while exporting users.", exception)


@register_tool("get_location_bookings")
@tool(
    args_schema=LocationBookingsInput,
    name_or_callable="Standort-Buchungen-anzeigen",
    description="Lists bookings for a specific Flexopus location.",
)
async def get_location_bookings(
    location_id: int, from_date: str, to_date: str
) -> list[LocationBookingsResponse] | dict[str, Any]:
    try:
        params = {"from": from_date, "to": to_date}
        payload = await _client().get(f"/locations/{location_id}/bookings", params=params)
        return [LocationBookingsResponse.model_validate(item) for item in payload]
    except RuntimeError as exception:
        return _error_payload(
            "Flexopus returned an error while fetching location bookings.", exception
        )


@register_tool("get_location_bookables")
@tool(
    args_schema=LocationIdInput,
    name_or_callable="Standort-Buchbare-anzeigen",
    description="Lists bookable resources for a specific Flexopus location.",
)
async def get_location_bookables(location_id: int) -> list[LocationBookable] | dict[str, Any]:
    try:
        payload = await _client().get(f"/locations/{location_id}/bookables")
        return [LocationBookable.model_validate(item) for item in payload]
    except RuntimeError as exception:
        return _error_payload(
            "Flexopus returned an error while fetching location bookables.", exception
        )


@register_tool("get_location_bookables_occupancy")
@tool(
    args_schema=LocationOccupancyInput,
    name_or_callable="Standort-Auslastung-anzeigen",
    description="Lists occupancy information for all bookables in a location.",
)
async def get_location_bookables_occupancy(
    location_id: int, details: bool = False
) -> list[LocationBookableOccupancy] | dict[str, Any]:
    try:
        params = {"details": str(details).lower()} if details else None
        payload = await _client().get(
            f"/locations/{location_id}/bookables/occupancy",
            params=params,
        )
        return [LocationBookableOccupancy.model_validate(item) for item in payload]
    except RuntimeError as exception:
        return _error_payload(
            "Flexopus returned an error while fetching location occupancy.", exception
        )


@register_tool("get_bookable_availability")
@tool(
    args_schema=BookableAvailabilityInput,
    name_or_callable="Buchbare-Verfuegbarkeit-anzeigen",
    description="Lists available bookables for a time range and optional filters.",
)
async def get_bookable_availability(
    from_date: str,
    to_date: str,
    location_id: int | None = None,
    building_id: int | None = None,
    occupied: bool | None = None,
    tags: list[str] | None = None,
    capacity: int | None = None,
    per_page: int | None = None,
) -> list[BookableAvailabilityBookable] | dict[str, Any]:
    body: dict[str, Any] = {
        "from": from_date,
        "to": to_date,
        "location_id": location_id,
        "building_id": building_id,
        "occupied": occupied,
        "tags": tags,
        "capacity": capacity,
        "per_page": per_page,
    }
    body = {key: value for key, value in body.items() if value not in (None, "")}

    try:
        payload = await _client().post("/bookables/availability", json_body=body)
        return [BookableAvailabilityBookable.model_validate(item) for item in payload]
    except RuntimeError as exception:
        return _error_payload(
            "Flexopus returned an error while checking bookable availability.", exception
        )


@register_tool("get_bookable_bookings")
@tool(
    args_schema=BookableIdInput,
    name_or_callable="Buchbare-Buchungen-anzeigen",
    description="Lists bookings for a specific bookable.",
)
async def get_bookable_bookings(
    bookable_id: int, from_date: str, to_date: str
) -> list[BookableBookingResponse] | dict[str, Any]:
    try:
        params = {"from": from_date, "to": to_date}
        payload = await _client().get(f"/bookables/{bookable_id}/bookings", params=params)
        return [BookableBookingResponse.model_validate(item) for item in payload]
    except RuntimeError as exception:
        return _error_payload(
            "Flexopus returned an error while fetching bookable bookings.", exception
        )


# TODO validate current user
@register_tool("create_booking", approval_required=True, hitl_description=_describe_booking_create)
@tool(
    args_schema=BookingCreateInput,
    name_or_callable=BOOKING_CREATE_TOOL,
    description="Creates a Flexopus booking. Requires approval before execution.",
)
async def create_booking(
    bookable_id: int,
    to_time: str,
    user_id: int,
    location_id: int,
    from_time: str | None = None,
    guest_email: str | None = None,
    guest_name: str | None = None,
    booking_info: str | None = None,
    user_vehicle_id: int | None = None,
) -> list[BookableBookingResponse] | dict[str, Any]:
    try:
        body: dict[str, Any] = {
            "bookable_id": bookable_id,
            "from_time": from_time,
            "to_time": to_time,
            "user_id": user_id,
            "location_id": location_id,
            "guest_email": guest_email,
            "guest_name": guest_name,
            "booking_info": booking_info,
            "user_vehicle_id": user_vehicle_id,
        }

        body = {key: value for key, value in body.items() if value not in (None, "")}

        payload = await _client().post("/bookings", json_body=body)
        return [BookableBookingResponse.model_validate(item) for item in payload]
    except RuntimeError as exception:
        return _error_payload("Flexopus returned an error while creating a booking.", exception)


# TODO: validate current user
@register_tool("delete_booking", approval_required=True, hitl_description=_describe_booking_delete)
@tool(
    args_schema=BookingDeleteInput,
    name_or_callable=BOOKING_DELETE_TOOL,
    description="Deletes a Flexopus booking. Requires approval before execution.",
)
async def delete_booking(booking_id: int, booking_summary: str = "") -> dict[str, Any]:
    try:
        return await _client().delete(f"/bookings/{booking_id}")
    except RuntimeError as exception:
        return _error_payload("Flexopus returned an error while deleting a booking.", exception)
