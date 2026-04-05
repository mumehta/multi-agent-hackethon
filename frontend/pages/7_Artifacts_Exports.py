import json

import streamlit as st

from utils.api_client import ApiClientError
from utils.formatters import dataframe_from_records, safe_json
from utils.state import require_selected_run
from utils.view_helpers import setup_page, show_api_error


client = setup_page("Artifacts and Exports", "📦")

st.title("Artifacts and Export")

run_id = require_selected_run()
if not run_id:
    st.stop()

try:
    artifacts = client.get_artifacts(run_id)
    export_json = client.export_json(run_id)
    export_markdown = client.export_markdown(run_id)
except ApiClientError as exc:
    show_api_error(exc)
    st.stop()

left, right = st.columns([2, 1])

with left:
    st.subheader("Artifacts")
    if artifacts:
        table_rows = []
        for item in artifacts:
            table_rows.append(
                {
                    "artifact_id": item.get("artifact_id"),
                    "name": item.get("name"),
                    "type": item.get("type"),
                    "size_bytes": item.get("size_bytes"),
                    "created_at": item.get("created_at"),
                    "description": item.get("description"),
                }
            )
        st.dataframe(dataframe_from_records(table_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No artifacts available.")

with right:
    st.subheader("Exports")
    st.download_button(
        "Download JSON Export",
        data=json.dumps(export_json, indent=2, default=str),
        file_name=f"{run_id}-export.json",
        mime="application/json",
    )
    st.download_button(
        "Download Markdown Export",
        data=export_markdown,
        file_name=f"{run_id}-report.md",
        mime="text/markdown",
    )

st.subheader("Markdown Preview")
if export_markdown:
    st.markdown(export_markdown)
else:
    st.info("No markdown export available.")

if artifacts:
    artifact_choice = st.selectbox("Preview artifact metadata", options=[item["artifact_id"] for item in artifacts])
    selected = next(item for item in artifacts if item["artifact_id"] == artifact_choice)
    st.code(safe_json(selected), language="json")
