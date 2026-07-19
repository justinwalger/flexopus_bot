"""Tests for the human-in-the-loop interrupt description builders."""

from llm.tools.formatting import _describe_booking_create, _describe_booking_delete


def _tool_call(args: dict) -> dict:
    return {"args": args}


class TestDescribeBookingCreate:
    def test_full_args_joins_all_parts_in_order(self):
        args = {
            "from_time": "2026-07-18T09:00",
            "to_time": "2026-07-18T10:00",
            "bookable_id": 5,
            "location_id": 3,
            "user_id": 42,
            "booking_info": "Team sync",
            "guest_name": "Jane Doe",
            "guest_email": "jane@example.com",
        }

        result = _describe_booking_create(_tool_call(args), None, None)

        assert result == (
            "Buchung anlegen | von 2026-07-18T09:00 | bis 2026-07-18T10:00 | "
            "Bookable 5 | Location 3 | User 42 | Info: Team sync | "
            "Gast: Jane Doe | E-Mail: jane@example.com"
        )

    def test_empty_args_returns_only_the_header(self):
        result = _describe_booking_create(_tool_call({}), None, None)

        assert result == "Buchung anlegen"

    def test_missing_optional_fields_are_omitted(self):
        args = {"from_time": "2026-07-18T09:00", "bookable_id": 5}

        result = _describe_booking_create(_tool_call(args), None, None)

        assert result == "Buchung anlegen | von 2026-07-18T09:00 | Bookable 5"

    def test_zero_valued_ids_are_still_included(self):
        args = {"bookable_id": 0, "location_id": 0, "user_id": 0}

        result = _describe_booking_create(_tool_call(args), None, None)

        assert result == "Buchung anlegen | Bookable 0 | Location 0 | User 0"

    def test_whitespace_only_optional_text_fields_are_omitted(self):
        args = {
            "booking_info": "   ",
            "guest_name": "\t",
            "guest_email": "\n",
        }

        result = _describe_booking_create(_tool_call(args), None, None)

        assert result == "Buchung anlegen"

    def test_optional_text_fields_are_stripped(self):
        args = {
            "booking_info": "  Team sync  ",
            "guest_name": "  Jane Doe  ",
            "guest_email": "  jane@example.com  ",
        }

        result = _describe_booking_create(_tool_call(args), None, None)

        assert result == (
            "Buchung anlegen | Info: Team sync | Gast: Jane Doe | E-Mail: jane@example.com"
        )


class TestDescribeBookingDelete:
    def test_uses_booking_summary_when_present(self):
        args = {"booking_summary": "Conference Room A, 2026-07-18 09:00-10:00", "booking_id": 7}

        result = _describe_booking_delete(_tool_call(args), None, None)

        assert result == "Conference Room A, 2026-07-18 09:00-10:00"

    def test_strips_booking_summary(self):
        args = {"booking_summary": "  Conference Room A  "}

        result = _describe_booking_delete(_tool_call(args), None, None)

        assert result == "Conference Room A"

    def test_falls_back_to_booking_id_when_summary_missing(self):
        args = {"booking_id": 7}

        result = _describe_booking_delete(_tool_call(args), None, None)

        assert result == "Buchung löschen (ID: 7)"

    def test_falls_back_to_booking_id_when_summary_is_whitespace(self):
        args = {"booking_summary": "   ", "booking_id": 7}

        result = _describe_booking_delete(_tool_call(args), None, None)

        assert result == "Buchung löschen (ID: 7)"

    def test_falls_back_with_none_id_when_neither_provided(self):
        result = _describe_booking_delete(_tool_call({}), None, None)

        assert result == "Buchung löschen (ID: None)"
