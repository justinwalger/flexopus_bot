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
