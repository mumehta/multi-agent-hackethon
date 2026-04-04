# src/multi_agent/integrations/jira.py
import requests
from requests.auth import HTTPBasicAuth
from typing import Dict, Any

def verify_jira_connectivity(ctx: Any) -> Dict[str, Any]:
    """
    Mirroring the Slack integration: Fetches config and tests the pipe.
    """
    email = ctx.fetch("JIRA_EMAIL")
    token = ctx.fetch("JIRA_API_TOKEN")
    base_url = ctx.fetch("JIRA_BASE_URL")
    
    if not all([email, token, base_url]):
        return {"status": "error", "message": "Missing Jira credentials in .env"}

    url = f"{base_url}/rest/api/3/myself"
    auth = HTTPBasicAuth(email, token)

    try:
        response = requests.get(url, auth=auth, timeout=10)
        return {
            "status": "success" if response.status_code == 200 else "failed",
            "status_code": response.status_code,
            "display_name": response.json().get("displayName") if response.status_code == 200 else None
        }
    except Exception as e:
        return {"status": "failed", "error": str(e)}