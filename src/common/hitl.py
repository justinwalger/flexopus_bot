"""Names of tools that require human-in-the-loop approval.

Shared between the tool definitions in `llm.tools.flexopus` (where the name is
registered via `@tool(name_or_callable=...)`) and the `HumanInTheLoopMiddleware`
config in `api.dependencies` (where the same name is used as an `interrupt_on`
key), so the two can't drift out of sync.
"""

BOOKING_CREATE_TOOL = "Buchung-anlegen"
BOOKING_DELETE_TOOL = "Buchung-loeschen"
