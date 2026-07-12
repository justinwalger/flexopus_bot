"""Streamlit entry point for RoxBot application.

design is inspired by https://github.com/streamlit/demo-ai-ai/blob/main/streamlit_app.py. thanks!
"""

import uuid

import streamlit as st
from htbuilder import div, styles
from htbuilder.units import rem
from pages.main import create_main_page

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
# Basic theming
st.set_page_config(page_title="RoxBot", page_icon="🏋️")
st.html(div(style=styles(font_size=rem(5), line_height=1))["🏋️"])

# import pages. curently only one page exists: main.py
create_main_page()
