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

# import pages. curently only one page exists: main.py
create_main_page()
