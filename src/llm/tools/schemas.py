from pydantic import BaseModel, Field


class FlexopusLocation(BaseModel):
    id: int
    code: str
    name: str


class FlexopusBookable(BaseModel):
    id: int
    location: FlexopusLocation
    name: str
    status: int
    tags: list[str]
    type: int


class FlexopusUser(BaseModel):
    email: str
    extensionAttributes: dict[str, str] | list[dict[str, str]]
    id: int
    name: str


class FlexopusUserExportRow(BaseModel):
    name: str
    email: str
    department: str
    function: str
    about: str
    notify: str
    groups: str
    roles: str
    timezone: str
    id: str
    created: str
    license_plates: str
    phone: str
    tags: str
    cost_center: str


class FlexopusBooking(BaseModel):
    bookable: FlexopusBookable
    from_: str = Field(alias="from")
    id: int
    livemap: str
    to: str | None = None
    user: FlexopusUser
    guest: dict[str, str] | str | None = None
    license_plate: str | None = None


class LocationBookingWindow(BaseModel):
    from_time: str
    to_time: str


class LocationBookable(BaseModel):
    id: int
    name: str
    type: int
    status: int
    capacity: int | None = None
    tags: list[str]


class LocationBookingUser(BaseModel):
    id: int
    name: str
    email: str
    extensionAttributes: dict[str, str] | list[dict[str, str]]


class LocationBookingsResponse(BaseModel):
    id: int
    from_: str = Field(alias="from")
    to: str | None = None
    livemap: str
    bookable: LocationBookable
    user: LocationBookingUser
    guest: dict[str, str] | None = None
    license_plate: str | None = None


class LocationBookableOccupancy(BaseModel):
    id: str
    location_name: str
    type: int
    name: str
    occupied: bool
    booking_current: LocationBookingWindow | None = None
    booking_next: LocationBookingWindow | None = None


class BookableBookingUser(BaseModel):
    id: int
    name: str
    email: str
    extensionAttributes: dict[str, str] | list[dict[str, str]]


class BookableBookingResponse(BaseModel):
    id: int
    from_: str = Field(alias="from")
    to: str | None = None
    livemap: str | None = None
    user: BookableBookingUser
    guest: dict[str, str] | str | None = None
    license_plate: str | None = None


class BookableAvailabilityBookable(BaseModel):
    id: int
    name: str
    type: int
    status: int
    capacity: int | None = None
    tags: list[str]
    occupied: bool


class UserEmailInput(BaseModel):
    user_email: str = Field(description="Email of the user to query")


class BuildingApiInput(BaseModel):
    """Input for building queries."""

    building_id: int = Field(description="ID of the building to query")
    to_date: str = Field(description="Must be a valid ISO date. Example: 2021-11-01T00:00:00Z")
    from_date: str = Field(description="Must be a valid ISO date. Example: 2021-11-03T00:00:00Z")


class LocationBookingsInput(BaseModel):
    location_id: int = Field(description="ID of the location to query")
    to_date: str = Field(description="Must be a valid ISO date. Example: 2021-11-03T00:00:00Z")
    from_date: str = Field(description="Must be a valid ISO date. Example: 2021-11-01T00:00:00Z")


class LocationIdInput(BaseModel):
    location_id: int = Field(description="ID of the location to query")


class LocationOccupancyInput(BaseModel):
    location_id: int = Field(description="ID of the location to query")
    details: bool = Field(default=False, description="Include current and next booking details")


class BookableAvailabilityInput(BaseModel):
    from_date: str = Field(description="Must be a valid ISO date. Example: 2021-11-01T00:00:00Z")
    to_date: str = Field(description="Must be a valid ISO date. Example: 2021-11-03T00:00:00Z")
    location_id: int | None = Field(default=None, description="The location's ID")
    building_id: int | None = Field(default=None, description="The building's ID")
    occupied: bool | None = Field(
        default=None, description="Only return occupied or free bookables"
    )
    tags: list[str] | None = Field(default=None, description="Filter for bookable tags")
    capacity: int | None = Field(
        default=None, ge=1, description="Filter for minimum bookable capacity"
    )
    per_page: int | None = Field(
        default=None,
        ge=1,
        le=100,
        description="Number of results per page",
    )


class BookableIdInput(BaseModel):
    bookable_id: int = Field(description="ID of the bookable to query")
    from_date: str = Field(description="Must be a valid ISO date. Example: 2021-11-01T00:00:00Z")
    to_date: str = Field(description="Must be a valid ISO date. Example: 2021-11-03T00:00:00Z")


class BookingCreateInput(BaseModel):
    bookable_id: int = Field(description="ID of the bookable to book")
    to_time: str = Field(description="Booking end time in ISO format")
    user_id: int = Field(description="ID of the user to book for")
    location_id: int = Field(description="ID of the location")
    from_time: str = Field(
        default="",
        description="Booking start time in ISO format. Leave empty to let Flexopus decide.",
    )
    guest_email: str = Field(default="", description="Guest email address")
    guest_name: str = Field(default="", description="Guest display name")
    booking_info: str = Field(default="", description="Optional booking note")
    user_vehicle_id: int | None = Field(
        default=None, description="Optional vehicle ID for parking bookings"
    )


class BookingDeleteInput(BaseModel):
    booking_id: int = Field(description="ID of the booking to delete")
    booking_summary: str = Field(
        default="",
        description="Human-readable booking summary for the approval dialog",
    )
