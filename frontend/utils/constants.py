DEFAULT_BACKEND_URL = "http://localhost:8000"
DEFAULT_DATA_MODE = "mock"
DATA_MODE_OPTIONS = ["mock", "live"]
REQUEST_TIMEOUT_SECONDS = 20

SEVERITY_ORDER = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
    "unknown": 0,
}

SEVERITY_EMOJI = {
    "critical": "🔴",
    "high": "🟠",
    "medium": "🟡",
    "low": "🟢",
    "unknown": "⚪",
}

SUPPORTED_UPLOAD_TYPES = ["log", "txt"]

SESSION_DEFAULTS = {
    "backend_base_url": DEFAULT_BACKEND_URL,
    "data_mode": DEFAULT_DATA_MODE,
    "selected_run_id": None,
    "latest_run_payload": None,
    "latest_incidents": [],
    "latest_timeline": [],
    "latest_root_cause": None,
    "config_status": None,
    "recent_runs": [],
    "secrets_form": {
        "jira_api_key": "",
        "slack_key": "",
        "anthropic_api_key": "",
        "openai_api_key": "",
    },
}
