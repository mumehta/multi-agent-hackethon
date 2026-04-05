import streamlit as st

from utils.api_client import ApiClientError
from utils.state import require_selected_run
from utils.view_helpers import setup_page, show_api_error


client = setup_page("Cookbook", "📘")

st.title("Cookbook View")

run_id = require_selected_run()
if not run_id:
    st.stop()

try:
    cookbook = client.get_cookbook(run_id)
    markdown_export = client.export_markdown(run_id)
except ApiClientError as exc:
    show_api_error(exc)
    st.stop()

markdown_text = cookbook.get("markdown") or markdown_export

if markdown_text:
    st.markdown(markdown_text)
    st.download_button(
        "Download Markdown",
        data=markdown_export,
        file_name=f"{run_id}-cookbook.md",
        mime="text/markdown",
    )
    with st.expander("Raw Markdown"):
        st.code(markdown_text, language="markdown")
else:
    st.info("No cookbook generated for this run.")
