"""Conversational (multi-turn) FlexBot evals.

Kept separate from `test_flexbot.py` because Confident AI rejects a test run
that mixes LLMTestCase and ConversationalTestCase results.

Slow, non-deterministic, costs tokens. Requires GOOGLE_API_KEY and valid
Flexopus credentials in the environment.
"""

import pytest
from conftest import run_turn
from deepeval import assert_test
from deepeval.metrics import ConversationalGEval
from deepeval.models import GeminiModel
from deepeval.test_case import ConversationalTestCase, MultiTurnParams, Turn

from llm.agent import ChatAgent

pytestmark = pytest.mark.eval


@pytest.mark.asyncio
async def test_multi_turn_conversation_remembers_the_users_name(
    chat_agent: ChatAgent, eval_model: GeminiModel
):
    thread_id = "multi-turn-demo"

    turn_1 = await run_turn(chat_agent, "Hallo, ich bin Martin Tester.", thread_id)
    assert "Name-speichern" in [tc.name for tc in turn_1.tools_called]

    turn_2 = await run_turn(chat_agent, "Welche Gebäude gibt es?", thread_id)
    tool_names = [tc.name for tc in turn_2.tools_called]
    assert "Gebaude-anzeigen" in tool_names
    assert "Name-speichern" not in tool_names, (
        "the agent already has the name from turn 1 and shouldn't ask again"
    )

    conversational_case = ConversationalTestCase(
        scenario="User introduces themselves, then asks an unrelated question.",
        expected_outcome="The assistant remembers the user's name without asking again.",
        turns=[
            Turn(role="user", content="Hallo, ich bin Martin Tester."),
            Turn(role="assistant", content=turn_1.answer),
            Turn(role="user", content="Welche Gebäude gibt es?"),
            Turn(role="assistant", content=turn_2.answer),
        ],
    )
    memory_metric = ConversationalGEval(
        model=eval_model,
        name="Conversational memory",
        criteria=(
            "Determine whether the assistant carried the name given in turn 1 "
            "forward appropriately, without asking the user to repeat it."
        ),
        threshold=0.5,
        evaluation_params=[MultiTurnParams.SCENARIO, MultiTurnParams.EXPECTED_OUTCOME],
    )
    assert_test(conversational_case, [memory_metric])
