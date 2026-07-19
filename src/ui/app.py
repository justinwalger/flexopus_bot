"""Streamlit entry point for application.

design is inspired by https://github.com/streamlit/demo-ai-ai/blob/main/streamlit_app.py. thanks!
"""

import uuid

import streamlit as st
from pages.main import create_main_page

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
# Basic theming
st.set_page_config(page_title="Flexopus Assistant", page_icon="🏢")

st.markdown(
    """
    <style>
        [data-testid="stSidebar"],
        [data-testid="stSidebarNav"],
        [data-testid="collapsedControl"] {
            display: none !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def _render_credentials_gate() -> None:
    """Ask the user for the Flexopus and Gemini credentials once at the start
    of the session, before any chat interaction is possible."""
    st.title("Flexopus Assistant", anchor=False)
    st.caption("Bitte gib deine Zugangsdaten ein, um eine neue Sitzung zu starten.")

    with st.form("credentials_form"):
        flexopus_api_key = st.text_input("Flexopus API Key", type="password")
        flexopus_url = st.text_input(
            "Flexopus URL", placeholder="https://example.flexopus.com/api/v1"
        )
        gemini_api_key = st.text_input("Gemini API Key", type="password")
        submitted = st.form_submit_button("Sitzung starten")

    if submitted:
        if not flexopus_api_key or not flexopus_url or not gemini_api_key:
            st.error("Bitte fülle alle Felder aus.")
            return

        st.session_state.flexopus_api_key = flexopus_api_key
        st.session_state.flexopus_url = flexopus_url
        st.session_state.gemini_api_key = gemini_api_key
        st.rerun()

    if st.button("Überspringen (Server-Zugangsdaten verwenden)"):
        st.session_state.flexopus_api_key = ""
        st.session_state.flexopus_url = ""
        st.session_state.gemini_api_key = ""
        st.rerun()


if "flexopus_api_key" not in st.session_state:
    _render_credentials_gate()
else:
    # import pages. curently only one page exists: main.py
    create_main_page()
