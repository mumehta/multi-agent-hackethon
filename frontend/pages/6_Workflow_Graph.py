import streamlit as st
import streamlit.components.v1 as components

from utils.api_client import ApiClientError
from utils.formatters import safe_json
from utils.view_helpers import setup_page, show_api_error


client = setup_page("Workflow Graph", "🕸️")

st.title("Workflow Graph")

try:
    workflow = client.get_workflow_mermaid()
except ApiClientError as exc:
    show_api_error(exc)
    st.stop()

st.subheader(workflow.get("title", "Workflow"))
st.code(workflow.get("mermaid", ""), language="mermaid")

view_url = workflow.get("view_url")
if view_url:
    st.link_button("Open Backend Mermaid View", view_url)
    if st.checkbox("Embed Mermaid View", value=False):
        components.iframe(view_url, height=600, scrolling=True)

with st.expander("Config Snapshot"):
    st.code(safe_json(workflow.get("config_snapshot", {})), language="json")
