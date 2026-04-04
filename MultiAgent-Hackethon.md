# Task: Multi-agent DevOps Incident Analysis Suite

## What it demonstrates

- An app that lets users upload ops logs for live analysis.
- Creates multiple agents:
  - Log reader/classifier agent (parses, categorizes, extracts fields).
  - Remediation agent (maps each detected issue to fixes/rationale).
  - Notification agent (pushes solutions directly to Slack channel).
  - Cookbook synthesizer agent (creates actionable checklists).
  - JIRA ticket agent (creates tickets for critical issues).
- Orchestrator manages flow between agents using LangGraph.
- Agents collaborate to reason over structured logs and recommend fixes, with traceable, actionable output via Slack/JIRA.

## Why it's ideal

- Leverages multi-agent orchestration, automated remediation, and integrated notifications.
- Perfect for DevOps, SRE, and incident management teams.
- Demonstrates how GenAI/Agents can automate incident review, remediation mapping, and cross-tool notification in a scalable workflow.

## Proposal

### To do

1. Logs can be uploaded.
2. Multiple agents do distinct jobs.
3. LangGraph orchestrates them.
4. Slack gets notified.
5. Jira ticket is created for critical issues.
6. Output is traceable and actionable.

LangGraph is a good fit because it is designed for stateful workflows and custom graph-based execution, including deterministic flows mixed with agentic behavior.

Slack incoming webhooks are enough for posting to a channel.

## User flow

Build a web app that:

1. Uploads a log file.
2. Clicks **Analyze**.
3. Backend parses logs.
4. LangGraph runs agents in sequence.
5. UI shows findings, severity, remediation, and cookbook.
6. Slack message is sent.
7. Jira ticket is created only for critical issues.

## MVP

### Frontend

Keep it dead simple:

- One page
- File upload
- **Analyze Logs** button
- Results panel with:
  - Parsed incidents
  - Severity
  - Remediation
  - Cookbook checklist
  - Slack status
  - Jira status

**Frontend Tech:** Streamlit or FastAPI + HTML

### Backend

- Python
- FastAPI for API
- LangGraph for orchestration
- Pydantic models for structured outputs
- OpenAI or another LLM for agent reasoning
- Slack incoming webhook
- Local JSON or SQLite for run history

## Agents in play

### 1. Log Reader / Classifier Agent

#### Responsibility

1. Parse raw log lines.
2. Extract timestamp, service, environment, error type, and probable root cause.
3. Classify issue type.
4. Assign severity.

#### Example categories

1. Authentication
2. Network/connectivity
3. Timeout
4. Resource exhaustion
5. Deployment/configuration
6. Dependency/service unavailable
7. Unknown

#### Output schema

```json
{
  "incidents": [
    {
      "id": "INC-001",
      "summary": "Database connection timeout in payment-service",
      "timestamp": "2026-04-04T10:21:13Z",
      "service": "payment-service",
      "environment": "prod",
      "category": "timeout",
      "severity": "critical",
      "evidence": ["line 15", "line 16"],
      "extracted_fields": {
        "status_code": "504",
        "host": "db-prod-1",
        "error_code": "ETIMEDOUT"
      }
    }
  ]
}
```

### 2. Remediation Agent

#### Responsibility

1. Map each incident to likely fixes.
2. Explain why those fixes make sense.
3. Rank fixes by confidence.

#### Output schema

```json
{
  "remediations": [
    {
      "incident_id": "INC-001",
      "root_cause_hypothesis": "Database unreachable or overloaded",
      "recommended_actions": [
        "Check DB connectivity from payment-service pod",
        "Review DB CPU and connection pool saturation",
        "Restart affected pod only if connectivity is restored"
      ],
      "rationale": "Repeated ETIMEDOUT and 504 errors suggest upstream DB latency or connectivity failure",
      "confidence": 0.86
    }
  ]
}
```

### 3. Cookbook Synthesizer Agent

#### Responsibility

1. Turn remediations into operator checklist.
2. Make it concrete and step-by-step.

#### Output schema

```json
{
  "cookbook": [
    {
      "incident_id": "INC-001",
      "title": "Payment service DB timeout response checklist",
      "steps": [
        "Verify database health metrics",
        "Check service-to-database network path",
        "Inspect recent deployments for config regressions",
        "Validate connection pool settings",
        "Escalate to DBA if DB saturation persists"
      ]
    }
  ]
}
```

### 4. Notification Agent

#### Responsibility

1. Build Slack-ready summary.
2. Send message.

This should not be a free-form reasoning agent. It should mostly format output and call Slack webhook. Slack incoming webhooks are the fastest path for a hackathon. They accept JSON payloads posted to a unique URL, and Slack documents that rate limiting can return HTTP 429, so handle that cleanly.

## Recommended LangGraph flow

```text
Upload Logs
   |
   v
Preprocessor Node
   |
   v
Log Reader / Classifier Agent
   |
   v
Remediation Agent
   |
   v
Cookbook Synthesizer Agent
   |
   +----> Notification Node -> Slack
   |
   +----> Conditional: if any critical incidents
                     |
                     v
               Jira Ticket Node
   |
   v
Final Aggregator Node
   |
   v
Return results to UI
```
