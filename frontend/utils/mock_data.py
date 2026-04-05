from copy import deepcopy
from datetime import datetime


MOCK_HEALTH = {
    "status": "ok",
    "service": "incident-analysis-backend",
    "timestamp": "2026-04-05T09:00:00Z",
}

MOCK_CONFIG_STATUS = {
    "llm": {
        "enabled": True,
        "provider": "openai",
        "model": "gpt-5.4-mini",
        "mock_mode": True,
    },
    "slack": {
        "enabled": True,
        "test_mode": True,
        "channel": "#incident-demo",
    },
    "jira": {
        "enabled": True,
        "test_mode": True,
        "project_key": "OPS",
    },
    "security": {
        "enabled": True,
    },
}

MOCK_RUNS = [
    {
        "run_id": "run-demo-001",
        "status": "completed",
        "filename": "checkout-errors.log",
        "created_at": "2026-04-05T08:20:00Z",
        "updated_at": "2026-04-05T08:23:00Z",
        "total_incidents": 3,
        "critical_incidents": 1,
        "grouped_incidents": 2,
        "slack_status": "sent",
        "jira_status": "created",
        "cookbook_generated": True,
    },
    {
        "run_id": "run-demo-002",
        "status": "completed",
        "filename": "payments-timeout.log",
        "created_at": "2026-04-05T07:10:00Z",
        "updated_at": "2026-04-05T07:14:00Z",
        "total_incidents": 2,
        "critical_incidents": 0,
        "grouped_incidents": 2,
        "slack_status": "suppressed",
        "jira_status": "not_created",
        "cookbook_generated": True,
    },
]

MOCK_INCIDENTS = {
    "run-demo-001": [
        {
            "incident_id": "inc-1001",
            "timestamp": "2026-04-05T08:20:11Z",
            "first_seen": "2026-04-05T08:19:58Z",
            "last_seen": "2026-04-05T08:21:47Z",
            "service": "checkout-service",
            "environment": "prod-au",
            "category": "database_connectivity",
            "summary": "Checkout requests failed after database connection pool exhaustion.",
            "severity": "critical",
            "priority": "p1",
            "confidence": 0.96,
            "count": 47,
            "trace_id": "trace-checkout-db-001",
            "correlation_id": "corr-release-112",
            "correlation_group": "grp-checkout-release-112",
            "related_services": ["checkout-service", "postgres-primary", "payments-service"],
            "related_incident_ids": ["inc-1002", "inc-1003"],
            "source_type": "application_log",
            "status_code": 500,
            "path": "/api/v1/checkout",
            "method": "POST",
            "sample_messages": [
                "psycopg timeout acquiring connection from pool",
                "checkout transaction aborted after db wait exceeded 30s",
            ],
            "remediation": {
                "title": "Stabilize database connectivity for checkout",
                "steps": [
                    "Rollback the latest checkout-service release.",
                    "Increase connection pool headroom temporarily.",
                    "Verify primary database latency and saturation.",
                ],
                "rationale": "The error burst starts immediately after deployment and clusters around connection acquisition timeouts.",
                "operator_summary": "Revert the release and restore database pool capacity before retrying traffic.",
                "source": "llm_cookbook",
            },
            "slack_status": "sent",
            "jira_status": "created",
        },
        {
            "incident_id": "inc-1002",
            "timestamp": "2026-04-05T08:21:03Z",
            "first_seen": "2026-04-05T08:20:45Z",
            "last_seen": "2026-04-05T08:22:10Z",
            "service": "payments-service",
            "environment": "prod-au",
            "category": "downstream_timeout",
            "summary": "Payments retries increased due to checkout dependency timeouts.",
            "severity": "high",
            "priority": "p2",
            "confidence": 0.88,
            "count": 19,
            "trace_id": "trace-payments-timeout-019",
            "correlation_id": "corr-release-112",
            "correlation_group": "grp-checkout-release-112",
            "related_services": ["payments-service", "checkout-service"],
            "related_incident_ids": ["inc-1001"],
            "source_type": "application_log",
            "status_code": 504,
            "path": "/api/v1/payments/charge",
            "method": "POST",
            "sample_messages": [
                "upstream checkout timeout after 10s",
                "retry budget exceeded for payment confirmation",
            ],
            "remediation": {
                "title": "Reduce payment retries until upstream stabilizes",
                "steps": [
                    "Throttle automated retries.",
                    "Monitor dependency latency from payments to checkout.",
                ],
                "rationale": "The payment failures are downstream symptoms of the checkout outage.",
                "operator_summary": "Treat this as secondary impact; focus recovery on checkout and database stability.",
                "source": "llm_cookbook",
            },
            "slack_status": "sent",
            "jira_status": "created",
        },
        {
            "incident_id": "inc-1003",
            "timestamp": "2026-04-05T08:22:01Z",
            "first_seen": "2026-04-05T08:21:49Z",
            "last_seen": "2026-04-05T08:23:00Z",
            "service": "edge-gateway",
            "environment": "prod-au",
            "category": "error_rate_spike",
            "summary": "Gateway error rate spiked for checkout endpoints during the outage.",
            "severity": "medium",
            "priority": "p3",
            "confidence": 0.74,
            "count": 31,
            "trace_id": "trace-edge-spike-031",
            "correlation_id": "corr-release-112",
            "correlation_group": "grp-checkout-release-112",
            "related_services": ["edge-gateway", "checkout-service"],
            "related_incident_ids": ["inc-1001"],
            "source_type": "gateway_log",
            "status_code": 502,
            "path": "/checkout",
            "method": "POST",
            "sample_messages": [
                "upstream connect error or disconnect/reset before headers",
                "gateway returned 502 for checkout endpoint",
            ],
            "remediation": {
                "title": "Validate upstream recovery before clearing gateway alerts",
                "steps": [
                    "Confirm gateway 5xx rate returns to baseline.",
                    "Clear alert only after checkout success rate stabilizes.",
                ],
                "rationale": "Gateway failures map directly to the upstream checkout incident.",
                "operator_summary": "Observe gateway as an impact surface, not the origin.",
                "source": "rule_engine",
            },
            "slack_status": "sent",
            "jira_status": "created",
        },
    ],
    "run-demo-002": [
        {
            "incident_id": "inc-2001",
            "timestamp": "2026-04-05T07:10:22Z",
            "first_seen": "2026-04-05T07:10:01Z",
            "last_seen": "2026-04-05T07:12:12Z",
            "service": "payments-service",
            "environment": "prod-us",
            "category": "third_party_timeout",
            "summary": "External payment gateway latency caused elevated timeout volume.",
            "severity": "high",
            "priority": "p2",
            "confidence": 0.91,
            "count": 24,
            "trace_id": "trace-gateway-timeout-024",
            "correlation_id": "corr-vendor-latency",
            "correlation_group": "grp-vendor-latency",
            "related_services": ["payments-service", "vendor-gateway"],
            "related_incident_ids": ["inc-2002"],
            "source_type": "application_log",
            "status_code": 504,
            "path": "/api/v1/payments/charge",
            "method": "POST",
            "sample_messages": [
                "gateway auth request timed out after 8s",
                "vendor latency exceeded SLA threshold",
            ],
            "remediation": {
                "title": "Fail over payment gateway traffic",
                "steps": [
                    "Route new traffic to the secondary vendor.",
                    "Lower timeout threshold for early detection.",
                ],
                "rationale": "The evidence points to external dependency latency instead of internal saturation.",
                "operator_summary": "Move traffic to the backup gateway and verify recovery.",
                "source": "llm_cookbook",
            },
            "slack_status": "suppressed",
            "jira_status": "not_created",
        },
        {
            "incident_id": "inc-2002",
            "timestamp": "2026-04-05T07:11:10Z",
            "first_seen": "2026-04-05T07:10:58Z",
            "last_seen": "2026-04-05T07:13:02Z",
            "service": "notification-service",
            "environment": "prod-us",
            "category": "queue_backlog",
            "summary": "Payment receipt notifications backed up while payment processing slowed down.",
            "severity": "low",
            "priority": "p4",
            "confidence": 0.62,
            "count": 11,
            "trace_id": "trace-notify-backlog-011",
            "correlation_id": "corr-vendor-latency",
            "correlation_group": "grp-vendor-latency",
            "related_services": ["notification-service", "payments-service"],
            "related_incident_ids": ["inc-2001"],
            "source_type": "worker_log",
            "status_code": 202,
            "path": "/jobs/receipt",
            "method": "POST",
            "sample_messages": [
                "receipt delivery lag exceeded target",
                "notification queue depth reached 120",
            ],
            "remediation": {
                "title": "Drain notification backlog after payment recovery",
                "steps": [
                    "Pause nonessential notification jobs.",
                    "Increase worker concurrency once gateway stabilizes.",
                ],
                "rationale": "Backlog is a downstream consequence, not the triggering event.",
                "operator_summary": "Treat as follow-on impact and recover after payments normalize.",
                "source": "rule_engine",
            },
            "slack_status": "suppressed",
            "jira_status": "not_created",
        },
    ],
}

MOCK_TIMELINE = {
    "run-demo-001": [
        {
            "timestamp": "2026-04-05T08:19:58Z",
            "service": "checkout-service",
            "category": "deployment",
            "severity": "medium",
            "summary": "Release 112 deployed to checkout-service.",
            "correlation_group": "grp-checkout-release-112",
            "related_services": ["checkout-service"],
        },
        {
            "timestamp": "2026-04-05T08:20:11Z",
            "service": "checkout-service",
            "category": "database_connectivity",
            "severity": "critical",
            "summary": "Database pool exhaustion triggered checkout failures.",
            "correlation_group": "grp-checkout-release-112",
            "related_services": ["checkout-service", "postgres-primary"],
        },
        {
            "timestamp": "2026-04-05T08:21:03Z",
            "service": "payments-service",
            "category": "downstream_timeout",
            "severity": "high",
            "summary": "Payments began timing out while waiting on checkout responses.",
            "correlation_group": "grp-checkout-release-112",
            "related_services": ["payments-service", "checkout-service"],
        },
    ],
    "run-demo-002": [
        {
            "timestamp": "2026-04-05T07:10:22Z",
            "service": "payments-service",
            "category": "third_party_timeout",
            "severity": "high",
            "summary": "Primary payment vendor latency crossed timeout thresholds.",
            "correlation_group": "grp-vendor-latency",
            "related_services": ["payments-service", "vendor-gateway"],
        },
        {
            "timestamp": "2026-04-05T07:11:10Z",
            "service": "notification-service",
            "category": "queue_backlog",
            "severity": "low",
            "summary": "Receipt jobs accumulated while payment transactions slowed.",
            "correlation_group": "grp-vendor-latency",
            "related_services": ["notification-service", "payments-service"],
        },
    ],
}

MOCK_ROOT_CAUSE = {
    "run-demo-001": {
        "probable_category": "database_connectivity",
        "severity": "critical",
        "confidence": 0.95,
        "summary": "The most likely root cause is a checkout deployment that increased database pool contention and exhausted available connections.",
        "impacted_services": ["checkout-service", "payments-service", "edge-gateway"],
        "supporting_incident_ids": ["inc-1001", "inc-1002", "inc-1003"],
        "evidence": [
            "The first failure appears immediately after release 112.",
            "Checkout logs show connection acquisition timeouts before downstream failures.",
            "Payments and gateway errors share the same correlation group and start later.",
        ],
    },
    "run-demo-002": {
        "probable_category": "third_party_timeout",
        "severity": "high",
        "confidence": 0.9,
        "summary": "The most likely root cause is latency at the external payment gateway rather than an internal service regression.",
        "impacted_services": ["payments-service", "notification-service"],
        "supporting_incident_ids": ["inc-2001", "inc-2002"],
        "evidence": [
            "Timeouts concentrate on calls to the external vendor.",
            "Notification lag begins after payment retries increase.",
        ],
    },
}

MOCK_COOKBOOK = {
    "run-demo-001": """# Incident Cookbook

## Executive Summary
Checkout failures were triggered by database pool exhaustion immediately after release 112.

## First Actions
1. Roll back release 112.
2. Increase database pool headroom.
3. Confirm checkout success rate recovers.

## Validation
- Database wait time returns to baseline.
- Checkout 5xx falls below 1%.
- Payment retries normalize.
""",
    "run-demo-002": """# Incident Cookbook

## Executive Summary
Payment latency is most consistent with a third-party gateway timeout event.

## First Actions
1. Shift traffic to the backup gateway.
2. Reduce retry amplification.
3. Drain notification backlog after recovery.

## Validation
- Vendor timeout rate drops.
- Payment P95 returns to normal.
- Receipt queue depth stabilizes.
""",
}

MOCK_ARTIFACTS = {
    "run-demo-001": [
        {
            "artifact_id": "art-001",
            "name": "incident_summary.json",
            "type": "json",
            "size_bytes": 4096,
            "created_at": "2026-04-05T08:23:10Z",
            "description": "Normalized run summary payload.",
            "metadata": {"content_type": "application/json", "generator": "analysis_pipeline"},
        },
        {
            "artifact_id": "art-002",
            "name": "cookbook.md",
            "type": "markdown",
            "size_bytes": 1024,
            "created_at": "2026-04-05T08:23:12Z",
            "description": "Operator cookbook generated from incident cluster.",
            "metadata": {"content_type": "text/markdown", "generator": "llm_cookbook"},
        },
    ],
    "run-demo-002": [
        {
            "artifact_id": "art-101",
            "name": "incident_summary.json",
            "type": "json",
            "size_bytes": 3072,
            "created_at": "2026-04-05T07:14:09Z",
            "description": "Normalized run summary payload.",
            "metadata": {"content_type": "application/json", "generator": "analysis_pipeline"},
        }
    ],
}

MOCK_WORKFLOW = {
    "title": "Incident Analysis Workflow",
    "mermaid": """flowchart TD
    A[Upload Logs] --> B[Parse Events]
    B --> C[Cluster Incidents]
    C --> D[Build Timeline]
    C --> E[Generate Cookbook]
    D --> F[Root Cause Analysis]
    F --> G[Artifacts and Exports]
    E --> G
""",
    "config_snapshot": {
        "runtime": "mock",
        "graph_engine": "langgraph",
        "version": "demo-2026-04-05",
    },
    "view_url": "http://localhost:8000/api/v1/workflow/mermaid/view",
}

MOCK_TEST_RESPONSES = {
    "llm": {"status": "ok", "provider": "openai", "model": "gpt-5.4-mini", "latency_ms": 842},
    "slack": {"status": "ok", "channel": "#incident-demo", "test_mode": True},
    "jira": {"status": "ok", "project_key": "OPS", "test_mode": True},
}


def _build_run_detail(run_id: str) -> dict:
    run_summary = next((run for run in MOCK_RUNS if run["run_id"] == run_id), None)
    incidents = MOCK_INCIDENTS.get(run_id, [])
    if not run_summary:
        raise KeyError(run_id)
    payload = deepcopy(run_summary)
    payload["incidents"] = deepcopy(incidents)
    payload["timeline"] = deepcopy(MOCK_TIMELINE.get(run_id, []))
    payload["root_cause"] = deepcopy(MOCK_ROOT_CAUSE.get(run_id))
    payload["cookbook_markdown"] = MOCK_COOKBOOK.get(run_id, "")
    return payload


def list_runs() -> list[dict]:
    return deepcopy(MOCK_RUNS)


def get_run(run_id: str) -> dict:
    return _build_run_detail(run_id)


def get_incidents(run_id: str) -> list[dict]:
    return deepcopy(MOCK_INCIDENTS.get(run_id, []))


def get_timeline(run_id: str) -> list[dict]:
    return deepcopy(MOCK_TIMELINE.get(run_id, []))


def get_root_cause(run_id: str) -> dict | None:
    return deepcopy(MOCK_ROOT_CAUSE.get(run_id))


def get_cookbook(run_id: str) -> dict:
    return {"run_id": run_id, "markdown": MOCK_COOKBOOK.get(run_id, "")}


def get_artifacts(run_id: str) -> list[dict]:
    return deepcopy(MOCK_ARTIFACTS.get(run_id, []))


def get_workflow() -> dict:
    return deepcopy(MOCK_WORKFLOW)


def build_export_json(run_id: str) -> dict:
    return {
        "run": get_run(run_id),
        "incidents": get_incidents(run_id),
        "timeline": get_timeline(run_id),
        "root_cause": get_root_cause(run_id),
        "artifacts": get_artifacts(run_id),
    }


def build_export_markdown(run_id: str) -> str:
    root_cause = get_root_cause(run_id) or {}
    incidents = get_incidents(run_id)
    lines = [
        f"# Incident Report: {run_id}",
        "",
        "## Root Cause",
        root_cause.get("summary", "No summary available."),
        "",
        "## Evidence",
    ]
    for item in root_cause.get("evidence", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Incidents"])
    for incident in incidents:
        lines.append(f"- {incident['incident_id']}: {incident['summary']} ({incident['severity']})")
    return "\n".join(lines)


def create_uploaded_run(filename: str) -> dict:
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    run_id = f"run-upload-{timestamp}"
    template_id = "run-demo-001"
    template_run = get_run(template_id)
    new_run = {
        "run_id": run_id,
        "status": "uploaded",
        "filename": filename,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "total_incidents": 0,
        "critical_incidents": 0,
        "grouped_incidents": 0,
        "slack_status": "pending",
        "jira_status": "pending",
        "cookbook_generated": False,
    }
    MOCK_RUNS.insert(0, new_run)
    MOCK_INCIDENTS[run_id] = template_run["incidents"]
    MOCK_TIMELINE[run_id] = template_run["timeline"]
    MOCK_ROOT_CAUSE[run_id] = template_run["root_cause"]
    MOCK_COOKBOOK[run_id] = template_run["cookbook_markdown"]
    MOCK_ARTIFACTS[run_id] = deepcopy(MOCK_ARTIFACTS[template_id])
    return deepcopy(new_run)


def analyze_run(run_id: str) -> dict:
    incidents = MOCK_INCIDENTS.get(run_id, [])
    for run in MOCK_RUNS:
        if run["run_id"] == run_id:
            run["status"] = "completed"
            run["updated_at"] = datetime.utcnow().isoformat() + "Z"
            run["total_incidents"] = len(incidents)
            run["critical_incidents"] = len([item for item in incidents if item.get("severity") == "critical"])
            run["grouped_incidents"] = len({item.get("correlation_group") for item in incidents})
            run["slack_status"] = incidents[0].get("slack_status", "sent") if incidents else "not_sent"
            run["jira_status"] = incidents[0].get("jira_status", "not_created") if incidents else "not_created"
            run["cookbook_generated"] = True
            return get_run(run_id)
    raise KeyError(run_id)
