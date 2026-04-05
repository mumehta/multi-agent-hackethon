import streamlit as st

from utils.api_client import ApiClientError
from utils.data_access import load_run_bundle
from utils.formatters import format_timestamp, incident_table_dataframe, list_to_text, safe_json, severity_badge, severity_sort_value
from utils.state import require_selected_run
from utils.view_helpers import setup_page, show_api_error


client = setup_page("Incident Explorer", "🔎")

st.title("Incident Explorer")

run_id = require_selected_run()
if not run_id:
    st.stop()

if st.button("Refresh Incidents"):
    try:
        _, incidents, _, _ = load_run_bundle(client, run_id)
        st.success("Incident data refreshed.")
    except ApiClientError as exc:
        show_api_error(exc)

incidents = st.session_state.get("latest_incidents") or []
if not incidents:
    try:
        _, incidents, _, _ = load_run_bundle(client, run_id)
    except ApiClientError as exc:
        show_api_error(exc)
        st.stop()

severities = sorted({item.get("severity", "unknown") for item in incidents})
services = sorted({item.get("service", "") for item in incidents if item.get("service")})
categories = sorted({item.get("category", "") for item in incidents if item.get("category")})

f1, f2, f3, f4, f5 = st.columns(5)
severity_filter = f1.multiselect("Severity", options=severities)
service_filter = f2.multiselect("Service", options=services)
category_filter = f3.multiselect("Category", options=categories)
search_text = f4.text_input("Search text")
sort_by = f5.selectbox("Sort by", options=["severity", "confidence", "count"])

filtered = []
for item in incidents:
    if severity_filter and item.get("severity") not in severity_filter:
        continue
    if service_filter and item.get("service") not in service_filter:
        continue
    if category_filter and item.get("category") not in category_filter:
        continue
    if search_text:
        haystack = safe_json(item).lower()
        if search_text.lower() not in haystack:
            continue
    filtered.append(item)

if sort_by == "severity":
    filtered = sorted(filtered, key=lambda item: severity_sort_value(item.get("severity")), reverse=True)
elif sort_by == "confidence":
    filtered = sorted(filtered, key=lambda item: item.get("confidence", 0), reverse=True)
else:
    filtered = sorted(filtered, key=lambda item: item.get("count", 0), reverse=True)

st.subheader("Incident Summary")
if filtered:
    st.dataframe(incident_table_dataframe(filtered), use_container_width=True, hide_index=True)
else:
    st.info("No incidents match the current filters.")

st.subheader("Incident Cards")
for incident in filtered:
    label = f"{severity_badge(incident.get('severity'))} {incident.get('incident_id')} | {incident.get('service')}"
    with st.expander(label):
        a1, a2, a3, a4 = st.columns(4)
        a1.write(f"**Timestamp**: {format_timestamp(incident.get('timestamp'))}")
        a2.write(f"**First Seen**: {format_timestamp(incident.get('first_seen'))}")
        a3.write(f"**Last Seen**: {format_timestamp(incident.get('last_seen'))}")
        a4.write(f"**Count**: {incident.get('count')}")
        st.write(f"**Service**: {incident.get('service')}")
        st.write(f"**Environment**: {incident.get('environment')}")
        st.write(f"**Category**: {incident.get('category')}")
        st.write(f"**Summary**: {incident.get('summary')}")
        st.write(f"**Severity**: {incident.get('severity')}")
        st.write(f"**Priority**: {incident.get('priority')}")
        st.write(f"**Confidence**: {incident.get('confidence')}")
        st.write(f"**Trace ID**: {incident.get('trace_id') or '-'}")
        st.write(f"**Correlation ID**: {incident.get('correlation_id') or '-'}")
        st.write(f"**Correlation Group**: {incident.get('correlation_group') or '-'}")
        st.write(f"**Related Services**: {list_to_text(incident.get('related_services'))}")
        st.write(f"**Related Incident IDs**: {list_to_text(incident.get('related_incident_ids'))}")
        st.write(f"**Source Type**: {incident.get('source_type')}")
        st.write(f"**Status Code**: {incident.get('status_code')}")
        st.write(f"**Path**: {incident.get('path')}")
        st.write(f"**Method**: {incident.get('method')}")
        st.write(f"**Sample Messages**: {list_to_text(incident.get('sample_messages'))}")
        remediation = incident.get("remediation", {})
        st.write(f"**Remediation Title**: {remediation.get('title', '-')}")
        st.write(f"**Remediation Steps**: {list_to_text(remediation.get('steps'))}")
        st.write(f"**Remediation Rationale**: {remediation.get('rationale', '-')}")
        st.write(f"**Operator Summary**: {remediation.get('operator_summary', '-')}")
        st.write(f"**Remediation Source**: {remediation.get('source', '-')}")
        st.write(f"**Slack Status**: {incident.get('slack_status', '-')}")
        st.write(f"**Jira Status**: {incident.get('jira_status', '-')}")
