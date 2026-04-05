import streamlit as st

from utils.api_client import ApiClientError
from utils.data_access import load_dashboard_snapshot
from utils.formatters import runs_table_dataframe, safe_json
from utils.view_helpers import setup_page, show_api_error


client = setup_page("Incident Analysis Console", "🚨")

st.title("Incident Analysis Console")
st.caption("Streamlit frontend for incident upload, analysis, investigation, and exports.")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Overview")
    st.write(
        "Use the pages in the left navigation to upload logs, inspect incidents, review the cookbook, "
        "trace the timeline, inspect artifacts, and test integrations."
    )

with col2:
    st.subheader("Current Context")
    st.metric("Data Source", st.session_state["data_mode"].upper())
    st.metric("Selected Run", st.session_state.get("selected_run_id") or "None")

try:
    health, config, runs = load_dashboard_snapshot(client)
except ApiClientError as exc:
    show_api_error(exc)
else:
    st.subheader("Backend Snapshot")
    snap1, snap2, snap3 = st.columns(3)
    snap1.metric("Health", health.get("status", "unknown"))
    snap2.metric("LLM Provider", config.get("llm", {}).get("provider", "-"))
    snap3.metric("Recent Runs", len(runs))

    st.subheader("Recent Runs")
    if runs:
        st.dataframe(runs_table_dataframe(runs), use_container_width=True, hide_index=True)
    else:
        st.info("No runs available yet.")

with st.expander("Raw Status Payloads"):
    st.code(safe_json({"health": locals().get("health"), "config": locals().get("config")}), language="json")
