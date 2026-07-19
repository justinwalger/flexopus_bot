"""Tests for the non-Flexopus (basic) tools."""

from datetime import datetime

import pytest

from llm.tools.basic import get_current_day


@pytest.mark.asyncio
async def test_get_current_day_returns_current_datetime():
    before = datetime.now()

    result = await get_current_day.ainvoke({})

    after = datetime.now()

    assert isinstance(result, datetime)
    assert before <= result <= after
