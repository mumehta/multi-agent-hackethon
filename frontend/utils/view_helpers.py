from __future__ import annotations

import streamlit as st

from utils.api_client import ApiClient
from utils.state import init_session_state, render_mode_banner, render_shared_sidebar


def setup_page(title: str, icon: str) -> ApiClient:
    st.set_page_config(page_title=title, page_icon=icon, layout="wide")
    init_session_state()
    render_shared_sidebar()
    render_mode_banner()
    return ApiClient(
        base_url=st.session_state["backend_base_url"],
        mode=st.session_state["data_mode"],
        secrets=st.session_state.get("secrets_form", {}),
    )


def show_api_error(exc: Exception) -> None:
    st.error(str(exc))
