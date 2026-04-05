import streamlit as st

from utils.api_client import ApiClientError
from utils.data_access import load_dashboard_snapshot, load_run_bundle, refresh_runs
from utils.formatters import runs_table_dataframe, safe_json
from utils.state import set_selected_run, update_run_context
from utils.view_helpers import setup_page, show_api_error


client = setup_page("Home", "🏠")

st.title("Home / Dashboard")

action1, action2, action3, action4, action5 = st.columns(5)

if action1.button("Analyze Sample Log", use_container_width=True):
    with st.spinner("Running sample analysis..."):
        try:
            run_payload = client.analyze_sample()
            update_run_context(run_payload=run_payload, incidents=run_payload.get("incidents", []))
            set_selected_run(run_payload.get("run_id"))
            st.success(f"Sample analysis completed for {run_payload.get('run_id')}.")
        except ApiClientError as exc:
            show_api_error(exc)

if action2.button("Refresh Runs", use_container_width=True):
    try:
        refresh_runs(client)
        st.success("Runs refreshed.")
    except ApiClientError as exc:
        show_api_error(exc)

if action3.button("Test LLM", use_container_width=True):
    try:
        st.session_state["llm_test_result"] = client.test_llm()
        st.success("LLM test completed.")
    except ApiClientError as exc:
        show_api_error(exc)

if action4.button("Test Slack", use_container_width=True):
    try:
        st.session_state["slack_test_result"] = client.test_slack()
        st.success("Slack test completed.")
    except ApiClientError as exc:
        show_api_error(exc)

if action5.button("Test Jira", use_container_width=True):
    try:
        st.session_state["jira_test_result"] = client.test_jira()
        st.success("Jira test completed.")
    except ApiClientError as exc:
        show_api_error(exc)

try:
    health, config, runs = load_dashboard_snapshot(client)
except ApiClientError as exc:
    show_api_error(exc)
    st.stop()

top1, top2, top3, top4 = st.columns(4)
top1.metric("Backend Health", health.get("status", "unknown"))
top2.metric("LLM Enabled", "Yes" if config.get("llm", {}).get("enabled") else "No")
top3.metric("Slack Enabled", "Yes" if config.get("slack", {}).get("enabled") else "No")
top4.metric("Jira Enabled", "Yes" if config.get("jira", {}).get("enabled") else "No")

cfg1, cfg2 = st.columns([2, 1])
with cfg1:
    st.subheader("Config Status")
    llm = config.get("llm", {})
    slack = config.get("slack", {})
    jira = config.get("jira", {})
    security = config.get("security", {})
    st.write(
        f"LLM: enabled={llm.get('enabled')} | provider={llm.get('provider')} | "
        f"model={llm.get('model')} | mock_mode={llm.get('mock_mode')}"
    )
    st.write(f"Slack: enabled={slack.get('enabled')} | test_mode={slack.get('test_mode')}")
    st.write(f"Jira: enabled={jira.get('enabled')} | test_mode={jira.get('test_mode')}")
    st.write(f"Security enabled: {security.get('enabled')}")

with cfg2:
    st.subheader("Selected Run")
    st.code(st.session_state.get("selected_run_id") or "None")

st.subheader("Recent Runs")
if runs:
    st.dataframe(runs_table_dataframe(runs), use_container_width=True, hide_index=True)
    selected = st.selectbox("Open run", options=[run["run_id"] for run in runs], index=0)
    if st.button("Load Selected Run"):
        try:
            load_run_bundle(client, selected)
            st.success(f"Loaded {selected}.")
        except ApiClientError as exc:
            show_api_error(exc)
else:
    st.info("No recent runs available.")

st.subheader("API Credentials")
st.caption(
    "These fields are masked in the UI, kept only in the current Streamlit session, "
    "and forwarded to the backend as request headers only in live mode."
)

secrets_form = st.session_state.get("secrets_form", {})
cred1, cred2 = st.columns(2)
with cred1:
    jira_api_key = st.text_input(
        "JIRA API Key",
        value=secrets_form.get("jira_api_key", ""),
        type="password",
        placeholder="Enter JIRA API key",
    )
    slack_key = st.text_input(
        "Slack Key",
        value=secrets_form.get("slack_key", ""),
        type="password",
        placeholder="Enter Slack key",
    )
with cred2:
    anthropic_api_key = st.text_input(
        "Anthropic API Key",
        value=secrets_form.get("anthropic_api_key", ""),
        type="password",
        placeholder="Enter Anthropic API key",
    )
    openai_api_key = st.text_input(
        "OpenAI API Key",
        value=secrets_form.get("openai_api_key", ""),
        type="password",
        placeholder="Enter OpenAI API key",
    )

st.session_state["secrets_form"] = {
    "jira_api_key": jira_api_key,
    "slack_key": slack_key,
    "anthropic_api_key": anthropic_api_key,
    "openai_api_key": openai_api_key,
}

if st.session_state.get("data_mode") == "live":
    provided = [label for label, value in {
        "JIRA": jira_api_key,
        "Slack": slack_key,
        "Anthropic": anthropic_api_key,
        "OpenAI": openai_api_key,
    }.items() if value]
    st.info(
        "Live mode header forwarding is active. "
        f"Providers with values set: {', '.join(provided) if provided else 'none'}."
    )

with st.expander("Integration Test Payloads"):
    st.code(
        safe_json(
            {
                "llm": st.session_state.get("llm_test_result"),
                "slack": st.session_state.get("slack_test_result"),
                "jira": st.session_state.get("jira_test_result"),
            }
        ),
        language="json",
    )
