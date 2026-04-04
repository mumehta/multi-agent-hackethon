# Final Hackathon Plan - Multi-Agent DevOps Incident Analysis Suite

## 1. Project Objective

Build a web app that allows users to upload operational logs, analyze them through a multi-step LangGraph workflow, identify incidents, recommend remediations, generate operator checklists, notify Slack, and create Jira tickets for qualified critical issues.

The output must be structured, traceable, and actionable.

---

## 2. Final MVP Scope

The MVP will support:

- Log file upload
- Preprocessing and incident grouping
- Multiple reasoning agents with distinct responsibilities
- LangGraph orchestration
- Remediation recommendations
- Checklist generation
- Slack notification
- Jira ticket creation for qualified critical incidents
- Traceable output in UI
- Run history persistence

### Out of Scope for MVP

- Live log streaming
- Autonomous remediation execution
- Advanced RAG/vector search
- Multi-user auth and RBAC
- Slack interactivity
- Jira sync-back updates
- Multi-file cross-correlation
- Production-grade observability platform features

Do not expand beyond this.

---

## 3. Final Architecture

### Frontend
**Streamlit**

Single-page UI with:
- File uploader
- Analyze Logs button
- Run summary
- Incident table
- Incident detail view
- Remediation panel
- Cookbook checklist
- Slack/Jira status
- Run history

### Backend / App Layer
**Python application**

Components:
- Ingestion and preprocessing logic
- LangGraph workflow
- OpenAI-based structured reasoning agents
- Slack integration
- Jira integration
- SQLite persistence

### Core Building Blocks
- Ingestion node
- Preprocessing node
- Deduplication and grouping node
- Classifier agent
- Remediation agent
- Cookbook agent
- Slack notification node
- Jira decision and ticket node
- Persistence node
- Final aggregator node

---

## 4. Final Workflow

```text
User uploads log file
   |
   v
Ingestion Node
   - validate file
   - assign run_id
   - capture source metadata
   |
   v
Preprocessing Node
   - split log lines
   - normalize timestamps
   - extract obvious fields using rules/regex
   - chunk large inputs
   - enforce token/file limits
   |
   v
Deduplication & Grouping Node
   - merge repeated errors
   - cluster related lines
   - create incident candidates
   |
   v
Classifier Agent
   - classify issue category
   - assign severity
   - assign priority
   - summarize likely incident
   - attach evidence references
   |
   v
Remediation Agent
   - infer root cause hypothesis
   - recommend ranked actions
   - provide rationale
   - assign confidence score
   |
   v
Cookbook Agent
   - convert remediations into operator checklist
   |
   +----> Slack Notification Node
   |        - format Slack message
   |        - send webhook
   |        - capture delivery result
   |
   +----> Jira Decision + Ticket Node
   |        - create ticket only if:
   |          severity = critical
   |          confidence >= 0.75
   |          category != unknown
   |          evidence_count >= 2
   |
   v
Persistence Node
   - save runs, incidents, outputs, statuses
   |
   v
Final Aggregator Node
   - return structured results to Streamlit UI
```

---

## 5. Agent and Node Responsibilities

### A. Ingestion Node
Not an agent.

**Responsibilities:**
- Accept uploaded file
- Validate type and size
- Assign `run_id`
- Record filename and metadata

### B. Preprocessing Node
Not an agent.

**Responsibilities:**
- Split raw logs into lines
- Normalize timestamps
- Extract obvious fields
- Identify service/environment if possible
- Reduce noise before LLM reasoning

This is important. Raw parsing should not rely entirely on the LLM.

### C. Deduplication and Grouping Node
Not an agent.

**Responsibilities:**
- Merge repeated signatures
- Cluster related log lines
- Create incident candidates

Without this step, the app will generate duplicate incidents and look sloppy.

### D. Classifier Agent
Reasoning agent.

**Responsibilities:**
- Classify incident category
- Assign severity
- Assign priority
- Summarize incident
- Reference evidence
- Explain severity reason

**Supported categories:**
- Authentication
- Network/connectivity
- Timeout
- Resource exhaustion
- Deployment/configuration
- Dependency/service unavailable
- Unknown

### E. Remediation Agent
Reasoning agent.

**Responsibilities:**
- Map incidents to likely causes
- Suggest ranked remediation actions
- Explain rationale
- Provide confidence score
- Flag human review requirement

### F. Cookbook Agent
Reasoning agent.

**Responsibilities:**
- Convert remediation into checklist
- Make it operator-friendly
- Keep it concrete and stepwise

### G. Slack Notification Node
Integration node, not an agent.

**Responsibilities:**
- Build Slack-ready summary
- Send via webhook
- Handle errors gracefully
- Persist delivery status

### H. Jira Decision + Ticket Node
Integration node, not an agent.

**Responsibilities:**
- Apply ticket-creation gate
- Create Jira issue for qualified critical incidents
- Include evidence, remediation, and cookbook details
- Persist ticket metadata

### I. Persistence Node
Integration/system node.

**Responsibilities:**
- Store run metadata
- Store incidents
- Store remediations
- Store cookbook outputs
- Store Slack and Jira outcomes

### J. Final Aggregator Node
Integration/system node.

**Responsibilities:**
- Combine all results into one response payload
- Supply complete UI-ready output
- Preserve traceability

---

## 6. Severity, Priority, and Confidence Model

This part must stay exactly like this.

### Severity
Severity measures **operational or business impact**.

**Values:**
- `critical`
- `high`
- `medium`
- `low`
- `info`

**Suggested interpretation:**
- **critical** - Production outage, major service failure, core business flow broken
- **high** - Serious degradation, partial outage, repeated failures, urgent operational risk
- **medium** - Contained issue, moderate degradation, recoverable errors
- **low** - Isolated low-impact issue, warning-level problem
- **info** - Informational event, no immediate action required

### Priority
Priority measures **response urgency**.

**Values:**
- `P1`
- `P2`
- `P3`
- `P4`

**Mapping:**
- `critical -> P1`
- `high -> P2`
- `medium -> P3`
- `low/info -> P4`

### Confidence
Confidence measures **how certain the system is** about its diagnosis and remediation hypothesis.

**Range:**
- `0.0 - 1.0`

**Bands:**
- `>= 0.90` - Very high
- `0.75 - 0.89` - High
- `0.50 - 0.74` - Moderate
- `< 0.50` - Low

### Jira Ticket Creation Rule
Create Jira ticket only if:
- `severity == critical`
- `confidence >= 0.75`
- `category != "unknown"`
- `evidence_count >= 2`

This prevents the bad mistake of confusing model certainty with operational criticality.

---

## 7. Final Traceability Model

Every incident/result should include:

- `run_id`
- `incident_id`
- `source_file`
- `timestamp`
- `service`
- `environment`
- `category`
- `severity`
- `priority`
- `severity_reason`
- `evidence` with line numbers/snippets
- `root_cause_hypothesis`
- `recommended_actions`
- `rationale`
- `confidence`
- `confidence_band`
- `cookbook_steps`
- `slack_status`
- `jira_status`
- `jira_ticket_key` if created
- Created/updated timestamps

That is your audit trail.

---

## 8. Final Data Schemas

### Incident Schema

```json
{
  "id": "INC-001",
  "run_id": "RUN-20260404-001",
  "source_file": "payment_prod_logs.txt",
  "summary": "Database connection timeout in payment-service",
  "timestamp": "2026-04-04T10:21:13Z",
  "service": "payment-service",
  "environment": "prod",
  "category": "timeout",
  "severity": "critical",
  "priority": "P1",
  "severity_reason": "Repeated database timeouts are breaking a production payment flow",
  "evidence": [
    {
      "line_number": 15,
      "snippet": "ETIMEDOUT connecting to db-prod-1"
    },
    {
      "line_number": 16,
      "snippet": "504 returned by payment-service"
    }
  ],
  "extracted_fields": {
    "status_code": "504",
    "host": "db-prod-1",
    "error_code": "ETIMEDOUT"
  }
}
```

### Remediation Schema

```json
{
  "incident_id": "INC-001",
  "root_cause_hypothesis": "Database unreachable or overloaded",
  "recommended_actions": [
    {
      "action": "Check DB connectivity from payment-service pod",
      "priority": 1
    },
    {
      "action": "Review DB CPU and connection pool saturation",
      "priority": 2
    },
    {
      "action": "Restart affected pod only after connectivity is restored",
      "priority": 3
    }
  ],
  "rationale": "Repeated ETIMEDOUT and 504 errors suggest upstream DB latency or connectivity failure",
  "confidence": 0.86,
  "confidence_band": "high",
  "human_review_required": true
}
```

### Cookbook Schema

```json
{
  "incident_id": "INC-001",
  "title": "Payment service DB timeout response checklist",
  "steps": [
    "Verify database health metrics",
    "Check service-to-database network path",
    "Inspect recent deployments for config regressions",
    "Validate connection pool settings",
    "Escalate to DBA if saturation persists"
  ]
}
```

### Slack Status Schema

```json
{
  "run_id": "RUN-20260404-001",
  "incident_id": "INC-001",
  "status": "sent",
  "channel": "#incident-alerts",
  "timestamp": "2026-04-04T10:25:11Z"
}
```

### Jira Status Schema

```json
{
  "run_id": "RUN-20260404-001",
  "incident_id": "INC-001",
  "status": "created",
  "ticket_key": "OPS-142",
  "priority": "Highest"
}
```

---

## 9. Streamlit UI Plan

Keep it simple and functional.

### Section 1 - Upload
- File uploader
- Analyze Logs button

### Section 2 - Run Summary
Show:
- Run id
- Filename
- Total incidents
- Critical incidents count
- Slack status
- Jira tickets created

### Section 3 - Incident Table
Columns:
- Incident id
- Service
- Category
- Severity
- Priority
- Confidence
- Jira status

### Section 4 - Incident Detail Panel
For selected incident:
- Summary
- Timestamp
- Service/environment
- Evidence snippets
- Severity and reason
- Root cause hypothesis
- Recommended actions
- Cookbook checklist

### Section 5 - Run History
Show recent runs:
- Run id
- File name
- Timestamp
- Incident count
- Slack result
- Jira result

Do not waste time polishing visuals before the flow works.

---

## 10. Final Tech Stack

- **Frontend**: Streamlit
- **Language**: Python
- **Workflow orchestration**: LangGraph
- **Data validation**: Pydantic
- **LLM reasoning**: OpenAI structured outputs
- **Persistence**: SQLite
- **Slack integration**: Incoming webhook
- **Jira integration**: Jira REST API

That stack is enough for the hackathon.

---

## 11. Database Persistence Plan

Use SQLite with these logical tables:

- `runs`
- `incidents`
- `remediations`
- `cookbooks`
- `slack_notifications`
- `jira_tickets`

Persist at minimum:
- Run metadata
- File metadata
- Incident outputs
- Remediation outputs
- Cookbook outputs
- Slack delivery result
- Jira creation result
- Timestamps

SQLite is fine for MVP. Do not overengineer storage.

---

## 12. Build Plan and Execution Order

### Phase 1 - Foundations
1. Define supported sample log formats
2. Create Pydantic schemas
3. Create SQLite schema
4. Scaffold Streamlit page layout

### Phase 2 - Core Processing
5. Build ingestion node
6. Build preprocessing node
7. Build deduplication and grouping logic
8. Generate incident candidates

### Phase 3 - LangGraph Workflow
9. Build classifier agent
10. Build remediation agent
11. Build cookbook agent
12. Wire all stages in LangGraph
13. Add final aggregator

### Phase 4 - Integrations
14. Implement Slack webhook integration
15. Implement Jira gating and ticket creation
16. Persist all results to SQLite

### Phase 5 - Demo Hardening
17. Build incident detail view in Streamlit
18. Add run history panel
19. Test with 2 to 3 prepared sample logs
20. Refine prompts and outputs
21. Add graceful failure handling for Slack/Jira/API issues

This is the correct order. Anything else increases rework.

---

## 13. Team Task Split

If you have 4 people:

### Person 1 - UI/App
- Streamlit layout
- File upload flow
- Result rendering
- Run history

### Person 2 - Processing
- Preprocessing
- Extraction
- Deduplication/grouping
- Incident candidate generation

### Person 3 - Agents/Graph
- Prompts
- Structured outputs
- LangGraph orchestration
- Aggregator

### Person 4 - Integrations/Persistence
- SQLite
- Slack webhook
- Jira API
- Error handling
- Status tracking

If you have fewer people, combine UI with integrations and keep one person focused only on core workflow.

---

## 14. Demo Plan

Use a prepared log file containing 2 to 3 obvious incident types, for example:
- Database timeout
- Dependency unavailable
- Authentication failure

### Demo Sequence
1. Upload log file
2. Click Analyze Logs
3. Show grouped incidents
4. Open one critical incident
5. Show evidence, severity, priority, root cause, remediation, and cookbook
6. Show Slack notification status
7. Show Jira ticket created for critical incident
8. Show run history saved

Do not demo random noisy logs. That is how people sabotage themselves.

---

## 15. Key Risks and Mitigations

### Risk 1 - Log variability breaks parsing
**Mitigation:**
- Support only a few known log styles in MVP
- Prepare clean sample logs
- Use deterministic preprocessing first

### Risk 2 - Duplicate/noisy incidents
**Mitigation:**
- Dedup and cluster before classification
- Avoid line-by-line incident generation

### Risk 3 - Hallucinated fixes
**Mitigation:**
- Require evidence-backed rationale
- Expose confidence score
- Mark human review requirement
- Keep actions as recommendations, not automated actions

### Risk 4 - Slack/Jira setup wastes time
**Mitigation:**
- Configure integrations early
- Create mock mode fallback
- Store/display payload even if live integration fails

### Risk 5 - Scope creep
**Mitigation:**
- Ship the main flow first
- Add nothing new until end-to-end demo works

---

## 16. Final Acceptance Criteria

The MVP is complete only if it can:

- Accept a log file upload
- Preprocess logs into incident candidates
- Deduplicate and group repeated errors
- Classify incidents by category/severity/priority
- Recommend remediations with rationale and confidence
- Generate cookbook checklists
- Send Slack notifications
- Create Jira tickets for qualified critical incidents
- Store run history in SQLite
- Show evidence-backed traceable output in Streamlit

If one of those is missing, the MVP is not done.

---

## 17. Final Summary

### Final Architecture Decision
- **Frontend**: Streamlit
- **Reasoning agents**:
  - Classifier Agent
  - Remediation Agent
  - Cookbook Agent
- **System/integration nodes**:
  - Ingestion
  - Preprocessing
  - Deduplication/Grouping
  - Slack Notification
  - Jira Decision/Ticket
  - Persistence
  - Final Aggregator
- **Orchestration**: LangGraph
- **Persistence**: SQLite
- **Notifications**: Slack webhook
- **Ticketing**: Jira REST API

### Final Operating Rule
- Severity = impact
- Priority = urgency
- Confidence = model certainty

### Final Jira Gate
Create ticket only if:
- Severity is critical
- Confidence is at least 0.75
- Category is not unknown
- Evidence count is at least 2

This plan is now coherent, realistic, and demoable.