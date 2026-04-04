# tests/test_integrations.py
import pytest
from src.multi_agent.config import ctx
from src.multi_agent.integrations.slack import send_slack_alert
from src.multi_agent.integrations.jira import verify_jira_connectivity


def test_config_fetch():
    """Verify AppConfig is reading the .env correctly."""
    val = ctx.fetch("SLACK_WEBHOOK_URL")
    assert val is not None, "SLACK_WEBHOOK_URL is missing from .env"

def test_slack_webhook_delivery():
    """Actually send a message to Slack to verify the Webhook is active."""
    test_msg = "Wellington Workstation Check: Slack Pipe is Live! 🚀"
    
    # This calls your slack.py logic
    result = send_slack_alert(ctx, test_msg)
    
    # Assertions for a successful POST request
    assert result["status"] == "success", f"Slack delivery failed: {result.get('error')}"
    assert result["status_code"] == 200
    # tests/test_integrations.py

def test_jira_handshake():
    """Mirroring the Slack test: Verify Jira Identity via the integration module."""
    result = verify_jira_connectivity(ctx)
    
    # Assertions identical in style to Slack
    assert result["status"] == "success", f"Jira Auth failed: {result.get('status_code')}"
    assert result["status_code"] == 200
    assert result["display_name"] is not None