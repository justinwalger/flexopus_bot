import json
import os
from collections.abc import Iterator

import httpx


class BackendConnector:
    def __init__(self, api_url: str | None = None, timeout: float = 60.0) -> None:
        self.api_url = api_url or os.getenv("BACKEND_API_URL")
        if not self.api_url:
            raise ValueError("BACKEND_API_URL is not configured.")
        self.timeout = timeout

    def ask_backend(self, message: str, thread_id: str) -> Iterator[dict[str, str]]:
        try:
            with httpx.stream(
                "POST",
                f"{self.api_url}/chat",
                json={"message": message, "thread_id": thread_id},
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
    ) -> Iterator[dict[str, str]]:
        try:
            with httpx.stream(
                "POST",
                f"{self.api_url}/chat/resume",
                json={
                    "thread_id": thread_id,
                    "interrupt_id": interrupt_id,
                    "decisions": decisions,
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
