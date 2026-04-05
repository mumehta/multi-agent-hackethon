import streamlit as st

from utils.api_client import ApiClientError
from utils.constants import SUPPORTED_UPLOAD_TYPES
from utils.state import update_run_context
from utils.view_helpers import setup_page, show_api_error


client = setup_page("Upload and Analyze", "📤")

st.title("Upload and Analyze")
st.write("Upload a plain-text log file, create a run, and trigger analysis.")

uploaded_file = st.file_uploader("Upload log file", type=SUPPORTED_UPLOAD_TYPES)

if uploaded_file is not None:
    st.write(f"File name: `{uploaded_file.name}`")
    if st.button("Upload and Analyze", type="primary"):
        try:
            with st.spinner("Uploading log file..."):
                upload_result = client.upload_run(uploaded_file)
            run_id = upload_result.get("run_id")
            with st.spinner("Running incident analysis..."):
                run_payload = client.analyze_run(run_id)
                incidents = client.get_incidents(run_id)
                timeline = client.get_timeline(run_id)
                root_cause = client.get_root_cause(run_id)
            update_run_context(run_payload=run_payload, incidents=incidents, timeline=timeline, root_cause=root_cause)
            st.success(f"Analysis completed for `{run_id}`.")
        except ApiClientError as exc:
            show_api_error(exc)

run_payload = st.session_state.get("latest_run_payload")
if run_payload:
    st.subheader("Run Summary")
    s1, s2, s3, s4, s5, s6 = st.columns(6)
    s1.metric("Run ID", run_payload.get("run_id"))
    s2.metric("Status", run_payload.get("status"))
    s3.metric("Total Incidents", run_payload.get("total_incidents", 0))
    s4.metric("Critical Incidents", run_payload.get("critical_incidents", 0))
    s5.metric("Grouped Incidents", run_payload.get("grouped_incidents", 0))
    s6.metric("Cookbook", "Ready" if run_payload.get("cookbook_generated") else "Pending")
    s7, s8 = st.columns(2)
    s7.metric("Slack Status", run_payload.get("slack_status", "-"))
    s8.metric("Jira Status", run_payload.get("jira_status", "-"))
    st.info(
        "Next steps: open Incident Explorer, Cookbook, Timeline and Root Cause, "
        "Artifacts and Exports, or Workflow Graph from the left navigation."
    )
else:
    st.info("No uploaded run yet.")
