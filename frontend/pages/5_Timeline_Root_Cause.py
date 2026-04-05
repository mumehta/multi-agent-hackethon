import streamlit as st

from utils.api_client import ApiClientError
from utils.data_access import load_run_bundle
from utils.formatters import dataframe_from_records, format_timestamp, list_to_text, severity_badge
from utils.state import require_selected_run
from utils.view_helpers import setup_page, show_api_error


client = setup_page("Timeline and Root Cause", "🧭")

st.title("Timeline and Root Cause")

run_id = require_selected_run()
if not run_id:
    st.stop()

if st.button("Refresh Narrative"):
    try:
        _, _, timeline, root_cause = load_run_bundle(client, run_id)
        st.success("Narrative data refreshed.")
    except ApiClientError as exc:
        show_api_error(exc)

timeline = st.session_state.get("latest_timeline") or []
root_cause = st.session_state.get("latest_root_cause")

if not timeline:
    try:
        _, _, timeline, root_cause = load_run_bundle(client, run_id)
    except ApiClientError as exc:
        show_api_error(exc)
        st.stop()

left, right = st.columns([3, 2])

with left:
    st.subheader("Timeline")
    timeline_rows = []
    for item in timeline:
        timeline_rows.append(
            {
                "timestamp": format_timestamp(item.get("timestamp")),
                "service": item.get("service"),
                "category": item.get("category"),
                "severity": severity_badge(item.get("severity")),
                "summary": item.get("summary"),
                "correlation_group": item.get("correlation_group"),
                "related_services": list_to_text(item.get("related_services")),
            }
        )
    if timeline_rows:
        st.dataframe(dataframe_from_records(timeline_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No timeline available.")

with right:
    st.subheader("Root Cause Narrative")
    if root_cause:
        st.write(f"**Probable Category**: {root_cause.get('probable_category')}")
        st.write(f"**Severity**: {severity_badge(root_cause.get('severity'))}")
        st.write(f"**Confidence**: {root_cause.get('confidence')}")
        st.write(f"**Summary**: {root_cause.get('summary')}")
        st.write(f"**Impacted Services**: {list_to_text(root_cause.get('impacted_services'))}")
        st.write(f"**Supporting Incident IDs**: {list_to_text(root_cause.get('supporting_incident_ids'))}")
        st.write("**Evidence**")
        for item in root_cause.get("evidence", []):
            st.write(f"- {item}")
    else:
        st.info("No root cause summary available.")
