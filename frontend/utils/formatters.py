from __future__ import annotations

import json
from datetime import datetime

import pandas as pd

from utils.constants import SEVERITY_EMOJI, SEVERITY_ORDER


def normalize_severity(value: str | None) -> str:
    return (value or "unknown").lower()


def severity_badge(value: str | None) -> str:
    severity = normalize_severity(value)
    return f"{SEVERITY_EMOJI.get(severity, '⚪')} {severity.title()}"


def severity_sort_value(value: str | None) -> int:
    return SEVERITY_ORDER.get(normalize_severity(value), 0)


def safe_json(data: object) -> str:
    return json.dumps(data, indent=2, default=str)


def format_timestamp(value: str | None) -> str:
    if not value:
        return "-"
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.strftime("%Y-%m-%d %H:%M:%S UTC")
    except ValueError:
        return value


def list_to_text(values: list[str] | None) -> str:
    if not values:
        return "-"
    return ", ".join(values)


def dataframe_from_records(records: list[dict]) -> pd.DataFrame:
    if not records:
        return pd.DataFrame()
    return pd.DataFrame(records)


def incident_table_dataframe(incidents: list[dict]) -> pd.DataFrame:
    rows = []
    for item in incidents:
        rows.append(
            {
                "incident_id": item.get("incident_id"),
                "severity": severity_badge(item.get("severity")),
                "service": item.get("service"),
                "category": item.get("category"),
                "summary": item.get("summary"),
                "confidence": item.get("confidence"),
                "count": item.get("count"),
                "correlation_group": item.get("correlation_group"),
            }
        )
    return dataframe_from_records(rows)


def runs_table_dataframe(runs: list[dict]) -> pd.DataFrame:
    rows = []
    for item in runs:
        rows.append(
            {
                "run_id": item.get("run_id"),
                "status": item.get("status"),
                "filename": item.get("filename"),
                "created_at": format_timestamp(item.get("created_at")),
                "total_incidents": item.get("total_incidents"),
                "critical_incidents": item.get("critical_incidents"),
                "grouped_incidents": item.get("grouped_incidents"),
                "slack_status": item.get("slack_status"),
                "jira_status": item.get("jira_status"),
                "cookbook_generated": item.get("cookbook_generated"),
            }
        )
    return dataframe_from_records(rows)
