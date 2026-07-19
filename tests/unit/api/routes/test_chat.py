"""Example: API-layer test for the /api/chat route.

get_chat_service is called directly (not via FastAPI's Depends()), so
app.dependency_overrides won't intercept it - monkeypatch the name in the
route module's namespace instead.
"""

from fastapi.testclient import TestClient

import api.routes.chat as chat_route
from api.main import app


class FakeChatService:
    async def answer(self, message, thread_id):
        yield {"type": "ai", "content": "hello"}


def test_stream_chat_returns_sse_chunks(monkeypatch):
    monkeypatch.setattr(chat_route, "get_chat_service", lambda **kwargs: FakeChatService())

    with TestClient(app) as client:
        response = client.post(
            "/api/chat",
            json={
                "flexopus_api_key": "key",
                "flexopus_url": "https://flexopus.test",
                "gemini_api_key": "key",
                "thread_id": "t1",
                "message": "hi",
            },
        )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert response.text == 'data: {"type": "ai", "content": "hello"}\n\n'
