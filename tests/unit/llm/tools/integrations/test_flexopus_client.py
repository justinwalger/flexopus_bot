"""Example: HTTP-layer tests for FlexopusClient using respx to mock httpx."""

import httpx
import pytest
import respx

from llm.tools.integrations.flexopus_client import FlexopusClient


@pytest.mark.asyncio
async def test_get_unwraps_data_field():
    client = FlexopusClient(token="test-token", base_url="https://flexopus.test")

    with respx.mock:
        route = respx.get("https://flexopus.test/buildings").mock(
            return_value=httpx.Response(200, json={"data": [{"id": 1, "name": "HQ"}]})
        )

        result = await client.get("/buildings")

    assert route.called
    assert result == [{"id": 1, "name": "HQ"}]
    assert route.calls.last.request.headers["Authorization"] == "Bearer test-token"
