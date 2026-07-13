"""Flexopus HTTP client for authenticated GET and POST requests."""

from contextvars import ContextVar
from typing import Any

import httpx

from common.config import get_settings

# Holds the per-request Flexopus credentials collected from the user at the
# start of a chat session, so tool calls issued within that request can reach
# them without threading token/base_url through every tool function signature.
_session_credentials: ContextVar[tuple[str, str] | None] = ContextVar(
    "flexopus_session_credentials", default=None
)


def set_flexopus_credentials(token: str, base_url: str) -> None:
    """Bind the Flexopus credentials to use for tool calls made in the current request."""
    _session_credentials.set((token, base_url))


class FlexopusClient:
    def __init__(
        self, token: str | None = None, base_url: str | None = None, timeout: float = 15.0
    ):
        session = _session_credentials.get()
        session_token, session_base_url = session if session else (None, None)
        settings = get_settings()

        token = token or session_token or settings.flexopus_api_token
        if not token:
            raise ValueError("FLEXOPUS_API_TOKEN is not configured.")
        self.base_url = base_url or session_base_url or settings.flexopus_api_url
        if not self.base_url:
            raise ValueError("FLEXOPUS_API_URL is not configured.")
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        self.timeout = timeout

    async def get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}{path}", headers=self.headers, params=params
            )

        if response.is_error:
            raise RuntimeError(
                f"Flexopus returned an error while fetching data: {response.text[:500]}"
            )

        try:
            payload = response.json()
        except ValueError:
            return response.text

        if isinstance(payload, dict) and "data" in payload:
            return payload["data"]

        return payload

    async def post(self, path: str, *, json_body: dict[str, Any]) -> Any:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}{path}",
                headers={**self.headers, "Content-Type": "application/json"},
                json=json_body,
            )

        if response.is_error:
            raise RuntimeError(
                f"Flexopus returned an error while sending data: {response.text[:500]}"
            )

        try:
            payload = response.json()
        except ValueError:
            raise RuntimeError("Flexopus returned a non-JSON response.") from None

        if isinstance(payload, dict) and "data" in payload:
            return payload["data"]

        return payload

    async def delete(self, path: str) -> Any:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.delete(
                f"{self.base_url}{path}",
                headers=self.headers,
            )

        if response.is_error:
            raise RuntimeError(
                f"Flexopus returned an error while deleting data: {response.text[:500]}"
            )

        if response.status_code == 204:
            return {"success": True, "message": "Booking deleted successfully."}

        try:
            payload = response.json()
        except ValueError:
            return {"success": True, "message": "Booking deleted successfully."}

        if isinstance(payload, dict) and "data" in payload:
            return payload["data"]

        return payload
