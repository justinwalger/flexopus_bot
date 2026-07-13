import json
from collections.abc import Iterator

import httpx
from config import get_settings


class BackendConnector:
    def __init__(self, api_url: str | None = None, timeout: float = 60.0) -> None:
        self.api_url = api_url or get_settings().backend_api_url
        self.timeout = timeout

    def ask_backend(
        self,
        message: str,
        thread_id: str,
        flexopus_api_key: str,
        flexopus_url: str,
        gemini_api_key: str,
    ) -> Iterator[dict[str, str]]:
        try:
            with httpx.stream(
                "POST",
                f"{self.api_url}/chat",
                json={
                    "message": message,
                    "thread_id": thread_id,
                    "flexopus_api_key": flexopus_api_key,
                    "flexopus_url": flexopus_url,
                    "gemini_api_key": gemini_api_key,
                },
                timeout=self.timeout,
            ) as response:
                response.raise_for_status()

                for line in response.iter_lines():
                    if not line or not line.startswith("data: "):
                        continue

                    event = json.loads(line.removeprefix("data: "))
                    yield event
        except GeneratorExit:
            return

    def resume_backend(
        self,
        thread_id: str,
        interrupt_id: str,
        decisions: list[dict[str, str]],
        flexopus_api_key: str,
        flexopus_url: str,
        gemini_api_key: str,
    ) -> Iterator[dict[str, str]]:
        try:
            with httpx.stream(
                "POST",
                f"{self.api_url}/chat/resume",
                json={
                    "thread_id": thread_id,
                    "interrupt_id": interrupt_id,
                    "decisions": decisions,
                    "flexopus_api_key": flexopus_api_key,
                    "flexopus_url": flexopus_url,
                    "gemini_api_key": gemini_api_key,
                },
                timeout=self.timeout,
            ) as response:
                response.raise_for_status()

                for line in response.iter_lines():
                    if not line or not line.startswith("data: "):
                        continue

                    event = json.loads(line.removeprefix("data: "))
                    yield event
        except GeneratorExit:
            return
