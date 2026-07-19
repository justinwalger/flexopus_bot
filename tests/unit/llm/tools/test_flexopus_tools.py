"""Example: LangChain tool tests, mocking the HTTP layer (respx) rather than FlexopusClient
directly, so the test also exercises credential resolution + response parsing."""

import json

import httpx
import pytest
import respx

from llm.tools.flexopus import (
    create_booking,
    delete_booking,
    get_bookable_availability,
    get_bookable_bookings,
    get_building_bookings,
    get_location_bookables,
    get_location_bookables_occupancy,
    get_location_bookings,
    get_user_by_email,
    list_flexopus_buildings,
    list_flexopus_groups,
    list_flexopus_users_export,
)
from llm.tools.integrations.flexopus_client import set_flexopus_credentials


@pytest.mark.asyncio
async def test_list_flexopus_buildings_returns_payload():
    set_flexopus_credentials("test-token", "https://flexopus.test")

    with respx.mock:
        respx.get("https://flexopus.test/buildings").mock(
            return_value=httpx.Response(200, json={"data": [{"id": 1, "name": "HQ"}]})
        )

        result = await list_flexopus_buildings.ainvoke({})

    assert result == [{"id": 1, "name": "HQ"}]


@pytest.mark.asyncio
async def test_list_flexopus_buildings_returns_error_payload_on_failure():
    set_flexopus_credentials("test-token", "https://flexopus.test")

    with respx.mock:
        respx.get("https://flexopus.test/buildings").mock(
            return_value=httpx.Response(500, text="boom")
        )

        result = await list_flexopus_buildings.ainvoke({})

    assert result["error"] == "Flexopus returned an error while fetching buildings."
    assert "boom" in result["details"]


@pytest.mark.asyncio
async def test_get_building_bookings_returns_payload():
    set_flexopus_credentials("test-token", "https://flexopus.test")
    payload = {
        "building_id": 1,
        "from_date": "2021-11-01T00:00:00Z",
        "to_date": "2021-11-03T00:00:00Z",
    }
    booking_json = {
        "id": 1,
        "from": "2021-11-01T09:00:00Z",
        "to": "2021-11-01T10:00:00Z",
        "livemap": "https://flexopus.test/livemap/1",
        "bookable": {
            "id": 10,
            "name": "Desk 1",
            "status": 1,
            "tags": [],
            "type": 1,
            "location": {"id": 100, "code": "HQ", "name": "Headquarters"},
        },
        "user": {
            "id": 5,
            "name": "Jane Doe",
            "email": "jane@example.com",
            "extensionAttributes": {},
        },
    }

    with respx.mock:
        respx.get("https://flexopus.test/buildings/1/bookings").mock(
            return_value=httpx.Response(200, json=[booking_json])
        )

        result = await get_building_bookings.ainvoke(payload)

    assert [booking.model_dump(by_alias=True) for booking in result] == [
        {
            "bookable": booking_json["bookable"],
            "from": booking_json["from"],
            "id": booking_json["id"],
            "livemap": booking_json["livemap"],
            "to": booking_json["to"],
            "user": booking_json["user"],
            "guest": None,
            "license_plate": None,
        }
    ]


@pytest.mark.asyncio
async def test_list_flexopus_groups_returns_payload():
    set_flexopus_credentials("test-token", "https://flexopus.test")

    with respx.mock:
        respx.get("https://flexopus.test/groups").mock(
            return_value=httpx.Response(200, json={"data": [{"id": 1, "name": "Admins"}]})
        )

        result = await list_flexopus_groups.ainvoke({})

    assert result == [{"id": 1, "name": "Admins"}]


@pytest.mark.asyncio
async def test_get_user_by_email_returns_matches():
    set_flexopus_credentials("test-token", "https://flexopus.test")
    user_json = {
        "id": 5,
        "name": "Jane Doe",
        "email": "jane@example.com",
        "extensionAttributes": {},
    }

    with respx.mock:
        route = respx.get("https://flexopus.test/users/by-email/jane@example.com").mock(
            return_value=httpx.Response(200, json={"data": [user_json]})
        )

        result = await get_user_by_email.ainvoke({"user_email": "jane@example.com"})

    assert route.called
    assert [user.model_dump() for user in result] == [user_json]


@pytest.mark.asyncio
async def test_get_user_by_email_returns_error_payload_on_failure():
    set_flexopus_credentials("test-token", "https://flexopus.test")

    with respx.mock:
        respx.get("https://flexopus.test/users/by-email/jane@example.com").mock(
            return_value=httpx.Response(500, text="boom")
        )

        result = await get_user_by_email.ainvoke({"user_email": "jane@example.com"})

    assert result["error"] == "Flexopus returned an error while searching by email."
    assert "boom" in result["details"]


@pytest.mark.asyncio
async def test_list_flexopus_users_export_parses_csv():
    set_flexopus_credentials("test-token", "https://flexopus.test")
    csv_body = (
        "name,email,department,function,about,notify,groups,roles,timezone,"
        "id,created,license_plates,phone,tags,cost_center\r\n"
        "Jane Doe,jane@example.com,Engineering,Developer,,yes,Group1,Admin,"
        "Europe/Berlin,5,2021-01-01,ABC123,+491234567,tag1;tag2,CC1\r\n"
    )

    with respx.mock:
        route = respx.get("https://flexopus.test/users/export").mock(
            return_value=httpx.Response(200, text=csv_body)
        )

        result = await list_flexopus_users_export.ainvoke({})

    assert route.called
    assert route.calls.last.request.url.params["format"] == "csv"
    assert [row.model_dump() for row in result] == [
        {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "department": "Engineering",
            "function": "Developer",
            "about": "",
            "notify": "yes",
            "groups": "Group1",
            "roles": "Admin",
            "timezone": "Europe/Berlin",
            "id": "5",
            "created": "2021-01-01",
            "license_plates": "ABC123",
            "phone": "+491234567",
            "tags": "tag1;tag2",
            "cost_center": "CC1",
        }
    ]


@pytest.mark.asyncio
async def test_get_location_bookings_returns_payload():
    set_flexopus_credentials("test-token", "https://flexopus.test")
    booking_json = {
        "id": 1,
        "from": "2021-11-01T09:00:00Z",
        "to": "2021-11-01T10:00:00Z",
        "livemap": "https://flexopus.test/livemap/1",
        "bookable": {"id": 10, "name": "Desk 1", "status": 1, "tags": [], "type": 1},
        "user": {
            "id": 5,
            "name": "Jane Doe",
            "email": "jane@example.com",
            "extensionAttributes": {},
        },
    }

    with respx.mock:
        route = respx.get("https://flexopus.test/locations/100/bookings").mock(
            return_value=httpx.Response(200, json=[booking_json])
        )

        result = await get_location_bookings.ainvoke(
            {
                "location_id": 100,
                "from_date": "2021-11-01T00:00:00Z",
                "to_date": "2021-11-03T00:00:00Z",
            }
        )

    assert route.calls.last.request.url.params["from"] == "2021-11-01T00:00:00Z"
    assert route.calls.last.request.url.params["to"] == "2021-11-03T00:00:00Z"
    assert [booking.model_dump(by_alias=True) for booking in result] == [
        {
            "id": booking_json["id"],
            "from": booking_json["from"],
            "to": booking_json["to"],
            "livemap": booking_json["livemap"],
            "bookable": booking_json["bookable"],
            "user": booking_json["user"],
            "guest": None,
            "license_plate": None,
        }
    ]


@pytest.mark.asyncio
async def test_get_location_bookables_returns_payload():
    set_flexopus_credentials("test-token", "https://flexopus.test")
    bookable_json = {"id": 10, "name": "Desk 1", "type": 1, "status": 1, "capacity": 1, "tags": []}

    with respx.mock:
        respx.get("https://flexopus.test/locations/100/bookables").mock(
            return_value=httpx.Response(200, json=[bookable_json])
        )

        result = await get_location_bookables.ainvoke({"location_id": 100})

    assert [bookable.model_dump() for bookable in result] == [bookable_json]


@pytest.mark.asyncio
async def test_get_location_bookables_occupancy_sends_details_param():
    set_flexopus_credentials("test-token", "https://flexopus.test")
    occupancy_json = {
        "id": "10",
        "location_name": "HQ",
        "type": 1,
        "name": "Desk 1",
        "occupied": True,
        "booking_current": {"from_time": "09:00", "to_time": "10:00"},
        "booking_next": None,
    }

    with respx.mock:
        route = respx.get("https://flexopus.test/locations/100/bookables/occupancy").mock(
            return_value=httpx.Response(200, json=[occupancy_json])
        )

        result = await get_location_bookables_occupancy.ainvoke(
            {"location_id": 100, "details": True}
        )

    assert route.calls.last.request.url.params["details"] == "true"
    assert [item.model_dump() for item in result] == [occupancy_json]


@pytest.mark.asyncio
async def test_get_location_bookables_occupancy_omits_details_param_by_default():
    set_flexopus_credentials("test-token", "https://flexopus.test")

    with respx.mock:
        route = respx.get("https://flexopus.test/locations/100/bookables/occupancy").mock(
            return_value=httpx.Response(200, json=[])
        )

        await get_location_bookables_occupancy.ainvoke({"location_id": 100})

    assert "details" not in route.calls.last.request.url.params


@pytest.mark.asyncio
async def test_get_bookable_availability_omits_unset_filters_from_request_body():
    set_flexopus_credentials("test-token", "https://flexopus.test")
    bookable_json = {
        "id": 10,
        "name": "Desk 1",
        "type": 1,
        "status": 1,
        "capacity": 1,
        "tags": [],
        "occupied": False,
    }

    with respx.mock:
        route = respx.post("https://flexopus.test/bookables/availability").mock(
            return_value=httpx.Response(200, json=[bookable_json])
        )

        result = await get_bookable_availability.ainvoke(
            {
                "from_date": "2021-11-01T00:00:00Z",
                "to_date": "2021-11-03T00:00:00Z",
                "location_id": 100,
            }
        )

    sent_body = json.loads(route.calls.last.request.content)
    assert sent_body == {
        "from": "2021-11-01T00:00:00Z",
        "to": "2021-11-03T00:00:00Z",
        "location_id": 100,
    }
    assert [bookable.model_dump() for bookable in result] == [bookable_json]


@pytest.mark.asyncio
async def test_get_bookable_bookings_returns_payload():
    set_flexopus_credentials("test-token", "https://flexopus.test")
    booking_json = {
        "id": 1,
        "from": "2021-11-01T09:00:00Z",
        "to": "2021-11-01T10:00:00Z",
        "livemap": None,
        "user": {
            "id": 5,
            "name": "Jane Doe",
            "email": "jane@example.com",
            "extensionAttributes": {},
        },
    }

    with respx.mock:
        respx.get("https://flexopus.test/bookables/10/bookings").mock(
            return_value=httpx.Response(200, json=[booking_json])
        )

        result = await get_bookable_bookings.ainvoke(
            {
                "bookable_id": 10,
                "from_date": "2021-11-01T00:00:00Z",
                "to_date": "2021-11-03T00:00:00Z",
            }
        )

    assert [booking.model_dump(by_alias=True) for booking in result] == [
        {
            "id": booking_json["id"],
            "from": booking_json["from"],
            "to": booking_json["to"],
            "livemap": None,
            "user": booking_json["user"],
            "guest": None,
            "license_plate": None,
        }
    ]


@pytest.mark.asyncio
async def test_create_booking_omits_blank_optional_fields_from_request_body():
    set_flexopus_credentials("test-token", "https://flexopus.test")
    booking_json = {
        "id": 1,
        "from": "2021-11-01T09:00:00Z",
        "to": "2021-11-01T10:00:00Z",
        "livemap": None,
        "user": {
            "id": 7,
            "name": "Jane Doe",
            "email": "jane@example.com",
            "extensionAttributes": {},
        },
    }

    with respx.mock:
        route = respx.post("https://flexopus.test/bookings").mock(
            return_value=httpx.Response(200, json=[booking_json])
        )

        result = await create_booking.ainvoke(
            {
                "bookable_id": 10,
                "to_time": "2021-11-01T10:00:00Z",
                "user_id": 7,
                "location_id": 100,
            }
        )

    sent_body = json.loads(route.calls.last.request.content)
    assert sent_body == {
        "bookable_id": 10,
        "to_time": "2021-11-01T10:00:00Z",
        "user_id": 7,
        "location_id": 100,
    }
    assert [booking.model_dump(by_alias=True)["id"] for booking in result] == [1]


@pytest.mark.asyncio
async def test_create_booking_returns_error_payload_on_failure():
    set_flexopus_credentials("test-token", "https://flexopus.test")

    with respx.mock:
        respx.post("https://flexopus.test/bookings").mock(
            return_value=httpx.Response(422, text="conflict")
        )

        result = await create_booking.ainvoke(
            {
                "bookable_id": 10,
                "to_time": "2021-11-01T10:00:00Z",
                "user_id": 7,
                "location_id": 100,
            }
        )

    assert result["error"] == "Flexopus returned an error while creating a booking."
    assert "conflict" in result["details"]


@pytest.mark.asyncio
async def test_delete_booking_returns_success_message_on_204():
    set_flexopus_credentials("test-token", "https://flexopus.test")

    with respx.mock:
        respx.delete("https://flexopus.test/bookings/42").mock(return_value=httpx.Response(204))

        result = await delete_booking.ainvoke({"booking_id": 42})

    assert result == {"success": True, "message": "Booking deleted successfully."}


@pytest.mark.asyncio
async def test_delete_booking_returns_error_payload_on_failure():
    set_flexopus_credentials("test-token", "https://flexopus.test")

    with respx.mock:
        respx.delete("https://flexopus.test/bookings/42").mock(
            return_value=httpx.Response(404, text="not found")
        )

        result = await delete_booking.ainvoke({"booking_id": 42})

    assert result["error"] == "Flexopus returned an error while deleting a booking."
    assert "not found" in result["details"]
