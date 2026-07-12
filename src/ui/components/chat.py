from collections.abc import Iterator

import streamlit as st
from constants import AVATARS
from models import Message, Role


def _render_hitl_request(event: dict[str, str]) -> None:
    interrupt_id = event.get("interrupt_id", "")
    action_requests = event["action_requests"]

    with st.container(border=True):
        st.caption("Bestätige die Aktion oder lehne sie ab. Du kannst auch Feedback geben.")
        st.markdown(f"**Offene Tool-Aufrufe:** {len(action_requests)}")
        for index, action_request in enumerate(action_requests, start=1):
            st.markdown(f"**{index}.** {action_request['description']}")

        col1, col2 = st.columns(2)
        if col1.button("✅", key=f"approve-{interrupt_id}", help="Approve"):
            st.session_state.hitl_resume = {
                "interrupt_id": interrupt_id,
                "decisions": [{"type": "approve"} for _ in action_requests],
            }
            st.rerun()

        if col2.button("❌", key=f"reject-{interrupt_id}", help="Reject"):
            st.session_state.hitl_resume = {
                "interrupt_id": interrupt_id,
                "decisions": [
                    {"type": "reject", "message": "Rejected by user."} for _ in action_requests
                ],
            }
            st.rerun()


def write_response(role: Role, data_source: str | Iterator[dict[str, str]]):
    """Create response message and append to session state.
    params:
        role: the role (user, ai)
        data_source (str|generator):
            if string: print the string
            if generator: print the generator as a stream

    add messages to session state.

    """
    avatar = AVATARS.get(role)
    if role == "human":
        with st.chat_message(role, avatar=avatar):
            st.markdown(data_source)
            st.session_state.messages.append(Message(role=role, content=data_source))

    else:
        with st.chat_message(role, avatar=avatar):
            tool_placeholder = st.empty()
            message_placeholder = st.empty()

            full_response = ""
            for event in data_source:
                event_type = event.get("type")
                content = event.get("content", "")

                if event_type == "tool":
                    tool_placeholder.info(content)
                    continue

                if event_type == "interrupt":
                    st.session_state.hitl_pending = event
                    _render_hitl_request(event)
                    continue

                if event_type == "ai" and content:
                    if isinstance(content, str):
                        delta = content
                    elif isinstance(content, list):
                        delta = "".join(
                            item.get("text", "") for item in content if isinstance(item, dict)
                        )
                    else:
                        delta = str(content)

                    full_response += delta
                    message_placeholder.markdown(full_response + "▌")

            if full_response:
                message_placeholder.markdown(full_response)

        if full_response:
            st.session_state.messages.append(Message(role=role, content=full_response))


def render_pending_hitl() -> None:
    event = st.session_state.get("hitl_pending")
    if not event:
        return

    _render_hitl_request(event)


def consume_hitl_resume() -> dict[str, object] | None:
    resume = st.session_state.pop("hitl_resume", None)
    if not resume:
        return None

    pending = st.session_state.get("hitl_pending")
    if not pending:
        return None

    st.session_state.hitl_pending = None
    return {
        "interrupt_id": resume["interrupt_id"],
        "decisions": resume["decisions"],
    }


def display_message(message: Message):
    """Display message in chat based on role."""
    role = message.role
    avatar = AVATARS.get(role)
    with st.chat_message(role, avatar=avatar):
        st.markdown(message.content)
