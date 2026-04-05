import streamlit as st

from utils.api_client import ApiClientError
from utils.data_access import load_run_bundle, refresh_runs
from utils.formatters import runs_table_dataframe
from utils.view_helpers import setup_page, show_api_error


client = setup_page("Runs History", "🗂️")

st.title("Runs History")

if st.button("Reload Runs"):
    try:
        refresh_runs(client)
        st.success("Runs reloaded.")
    except ApiClientError as exc:
        show_api_error(exc)

runs = st.session_state.get("recent_runs") or []
if not runs:
    try:
        runs = refresh_runs(client)
    except ApiClientError as exc:
        show_api_error(exc)
        st.stop()

status_options = sorted({run.get("status", "unknown") for run in runs})
status_filter = st.multiselect("Filter by status", options=status_options)

filtered_runs = [run for run in runs if not status_filter or run.get("status") in status_filter]

if filtered_runs:
    st.dataframe(runs_table_dataframe(filtered_runs), use_container_width=True, hide_index=True)
    selected_run = st.selectbox("Select run", options=[run["run_id"] for run in filtered_runs])
    if st.button("Open Selected Run", type="primary"):
        try:
            load_run_bundle(client, selected_run)
            st.success(f"Loaded {selected_run}.")
        except ApiClientError as exc:
            show_api_error(exc)
else:
    st.info("No runs match the selected filter.")
