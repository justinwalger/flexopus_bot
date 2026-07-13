"""Main page of the app, used for interacting with the llm."""

import streamlit as st
from backend_connector import BackendConnector
from components.chat import (
    consume_hitl_resume,
    display_message,
    render_pending_hitl,
    write_response,
)
from constants import SUGGESTIONS

_connector = BackendConnector()


def handle_suggestion_change() -> None:
    st.session_state.pending_suggestion = st.session_state.selected_suggestion


def create_main_page():
    """Create main page."""
    title_row = st.container(
        horizontal=True,
        vertical_alignment="bottom",
    )

    with title_row:
        st.title(
            "Flexopus Assistant",
            anchor=False,
            width="stretch",
        )
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Ask for suggestions
    st.pills(
        label="Schnelleinstiege",
        label_visibility="collapsed",
        options=SUGGESTIONS.keys(),
        key="selected_suggestion",
        on_change=handle_suggestion_change,
    )

    # Container for chat history
    with st.container():
        for message in st.session_state.messages:
            display_message(message)

    if resume_payload := consume_hitl_resume():
        llm_generator = _connector.resume_backend(
            thread_id=st.session_state.thread_id,
            interrupt_id=resume_payload["interrupt_id"],
            decisions=resume_payload["decisions"],
            flexopus_api_key=st.session_state.flexopus_api_key,
            flexopus_url=st.session_state.flexopus_url,
            gemini_api_key=st.session_state.gemini_api_key,
        )
        write_response("ai", llm_generator)
    else:
        render_pending_hitl()

    # Flow for suggested questions
    pending_suggestion = st.session_state.get("pending_suggestion")
    if pending_suggestion:
        suggested_question = SUGGESTIONS[pending_suggestion]
        st.session_state.pending_suggestion = None
        write_response("human", suggested_question)
        llm_generator = _connector.ask_backend(
            message=suggested_question,
            thread_id=st.session_state.thread_id,
            flexopus_api_key=st.session_state.flexopus_api_key,
            flexopus_url=st.session_state.flexopus_url,
            gemini_api_key=st.session_state.gemini_api_key,
        )
        write_response("ai", llm_generator)

    # footer
    with title_row:

        def clear_conversation():
            st.session_state.messages = []

        st.button(
            "Neues Gespräch",
            icon=":material/refresh:",
            on_click=clear_conversation,
        )

    # Flow for human input
    if human_input := st.chat_input("Stelle eine Frage...", key="initial_question"):
        write_response("human", human_input)
        llm_generator = _connector.ask_backend(
            message=human_input,
            thread_id=st.session_state.thread_id,
            flexopus_api_key=st.session_state.flexopus_api_key,
            flexopus_url=st.session_state.flexopus_url,
            gemini_api_key=st.session_state.gemini_api_key,
        )
        write_response("ai", llm_generator)
