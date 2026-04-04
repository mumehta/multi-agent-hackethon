import requests
from typing import Dict, Any

def send_slack_alert(ctx: Any, message: str) -> Dict[str, Any]:
    """
    Integration that fetches its own config from the context.
    """
    webhook_url = ctx.fetch("SLACK_WEBHOOK_URL")
    
    if not webhook_url:
        return {"status": "error", "message": "Missing SLACK_WEBHOOK_URL"}

    payload = {"text": message}

    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        return {
            "status": "success" if response.status_code == 200 else "failed",
            "status_code": response.status_code
        }
    except Exception as e:
        return {"status": "failed", "error": str(e)}