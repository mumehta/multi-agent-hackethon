import streamlit as st

from utils.api_client import ApiClientError
from utils.formatters import safe_json
from utils.view_helpers import setup_page


client = setup_page("Integrations", "🔌")

st.title("Integration Status / Tools")

c1, c2, c3 = st.columns(3)

if c1.button("Test LLM", use_container_width=True):
    try:
        st.session_state["integration_result"] = {"type": "llm", "payload": client.test_llm()}
    except ApiClientError as exc:
        st.session_state["integration_result"] = {"type": "llm", "payload": {"error": str(exc)}}

if c2.button("Test Slack", use_container_width=True):
    try:
        st.session_state["integration_result"] = {"type": "slack", "payload": client.test_slack()}
    except ApiClientError as exc:
        st.session_state["integration_result"] = {"type": "slack", "payload": {"error": str(exc)}}

if c3.button("Test Jira", use_container_width=True):
    try:
        st.session_state["integration_result"] = {"type": "jira", "payload": client.test_jira()}
    except ApiClientError as exc:
        st.session_state["integration_result"] = {"type": "jira", "payload": {"error": str(exc)}}

result = st.session_state.get("integration_result")
if result:
    st.subheader(f"{result['type'].upper()} Response")
    payload = result["payload"]
    if isinstance(payload, dict) and payload.get("error"):
        st.error(payload["error"])
    st.code(safe_json(payload), language="json")
else:
    st.info("Run an integration test to inspect the backend response.")
