from __future__ import annotations

import streamlit as st

from utils.api_client import ApiClient
from utils.state import set_selected_run, update_run_context


def refresh_runs(client: ApiClient) -> list[dict]:
    runs = client.list_runs()
    st.session_state["recent_runs"] = runs
    return runs


def load_dashboard_snapshot(client: ApiClient) -> tuple[dict, dict, list[dict]]:
    health = client.health()
    config = client.config_status()
    runs = refresh_runs(client)
    st.session_state["config_status"] = config
    return health, config, runs


def load_run_bundle(client: ApiClient, run_id: str) -> tuple[dict, list[dict], list[dict], dict | None]:
    run_payload = client.get_run(run_id)
    incidents = client.get_incidents(run_id)
    timeline = client.get_timeline(run_id)
    root_cause = client.get_root_cause(run_id)
    set_selected_run(run_id)
    update_run_context(
        run_payload=run_payload,
        incidents=incidents,
        timeline=timeline,
        root_cause=root_cause,
    )
    return run_payload, incidents, timeline, root_cause
