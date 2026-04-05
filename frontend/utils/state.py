from __future__ import annotations

import streamlit as st

from utils.constants import DATA_MODE_OPTIONS, SESSION_DEFAULTS


def init_session_state() -> None:
    for key, value in SESSION_DEFAULTS.items():
        st.session_state.setdefault(key, value)


def set_selected_run(run_id: str | None) -> None:
    st.session_state["selected_run_id"] = run_id


def update_run_context(
    run_payload: dict | None = None,
    incidents: list | None = None,
    timeline: list | None = None,
    root_cause: dict | None = None,
) -> None:
    if run_payload is not None:
        st.session_state["latest_run_payload"] = run_payload
        if run_payload.get("run_id"):
            st.session_state["selected_run_id"] = run_payload["run_id"]
    if incidents is not None:
        st.session_state["latest_incidents"] = incidents
    if timeline is not None:
        st.session_state["latest_timeline"] = timeline
    if root_cause is not None:
        st.session_state["latest_root_cause"] = root_cause


def render_shared_sidebar() -> None:
    with st.sidebar:
        st.header("Connection")
        base_url = st.text_input("Backend URL", value=st.session_state["backend_base_url"])
        st.session_state["backend_base_url"] = base_url.strip() or st.session_state["backend_base_url"]
        mode = st.radio(
            "Data Source",
            options=DATA_MODE_OPTIONS,
            index=DATA_MODE_OPTIONS.index(st.session_state["data_mode"]),
            horizontal=True,
            help="Mock mode uses local sample payloads. Live mode calls the backend.",
        )
        st.session_state["data_mode"] = mode
        st.divider()
        st.caption(f"Selected run: `{st.session_state.get('selected_run_id') or 'none'}`")
        if st.button("Clear Selected Run", use_container_width=True):
            st.session_state["selected_run_id"] = None
            st.session_state["latest_run_payload"] = None
            st.session_state["latest_incidents"] = []
            st.session_state["latest_timeline"] = []
            st.session_state["latest_root_cause"] = None


def render_mode_banner() -> None:
    if st.session_state.get("data_mode") == "mock":
        st.warning(
            "MOCK MODE ACTIVE: This UI is using local sample payloads instead of the backend. "
            "Switch the sidebar to LIVE mode to call `http://localhost:8000`."
        )


def require_selected_run() -> str | None:
    run_id = st.session_state.get("selected_run_id")
    if not run_id:
        st.info("Select or create a run first. Use Home, Upload and Analyze, or Runs History.")
        return None
    return run_id
