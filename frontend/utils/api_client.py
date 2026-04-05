from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import requests

from utils.constants import REQUEST_TIMEOUT_SECONDS
from utils import mock_data


class ApiClientError(Exception):
    pass


@dataclass
class ApiClient:
    base_url: str
    mode: str = "mock"
    timeout: int = REQUEST_TIMEOUT_SECONDS
    secrets: dict[str, str] | None = None

    def _build_secret_headers(self) -> dict[str, str]:
        if self.mode != "live" or not self.secrets:
            return {}

        header_map = {
            "openai_api_key": "X-OpenAI-API-Key",
            "anthropic_api_key": "X-Anthropic-API-Key",
            "slack_key": "X-Slack-Key",
            "jira_api_key": "X-Jira-API-Key",
        }
        headers = {}
        for field_name, header_name in header_map.items():
            value = (self.secrets.get(field_name) or "").strip()
            if value:
                headers[header_name] = value
        return headers

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self.base_url.rstrip('/')}{path}"
        request_headers = dict(kwargs.pop("headers", {}) or {})
        request_headers.update(self._build_secret_headers())
        try:
            response = requests.request(method, url, timeout=self.timeout, headers=request_headers, **kwargs)
        except requests.RequestException as exc:
            raise ApiClientError(f"Request failed: {exc}") from exc

        content_type = response.headers.get("content-type", "")
        payload = None
        if "application/json" in content_type:
            try:
                payload = response.json()
            except json.JSONDecodeError as exc:
                raise ApiClientError(f"Invalid JSON response from {path}") from exc
        elif response.text:
            payload = response.text

        if response.status_code >= 400:
            if isinstance(payload, dict) and payload.get("error"):
                error = payload["error"]
                message = error.get("message", "Backend returned an error")
                code = error.get("code", response.status_code)
                request_path = error.get("path", path)
                raise ApiClientError(f"{code}: {message} ({request_path})")
            raise ApiClientError(f"{response.status_code}: {response.text or 'Request failed'}")
        return payload

    @staticmethod
    def _unwrap_list(payload: Any, list_keys: tuple[str, ...]) -> list[dict]:
        if payload is None:
            return []
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            for key in list_keys:
                value = payload.get(key)
                if isinstance(value, list):
                    return value
        raise ApiClientError("Unexpected list response shape from backend.")

    @staticmethod
    def _unwrap_dict(payload: Any, dict_keys: tuple[str, ...] = ()) -> dict:
        if payload is None:
            return {}
        if isinstance(payload, dict):
            for key in dict_keys:
                value = payload.get(key)
                if isinstance(value, dict):
                    return value
            return payload
        raise ApiClientError("Unexpected object response shape from backend.")

    @staticmethod
    def _unwrap_text(payload: Any, text_keys: tuple[str, ...] = ("markdown", "content", "text")) -> str:
        if payload is None:
            return ""
        if isinstance(payload, str):
            return payload
        if isinstance(payload, dict):
            for key in text_keys:
                value = payload.get(key)
                if isinstance(value, str):
                    return value
        raise ApiClientError("Unexpected text response shape from backend.")

    def health(self) -> dict:
        if self.mode == "mock":
            return mock_data.MOCK_HEALTH
        return self._unwrap_dict(self._request("GET", "/health"))

    def config_status(self) -> dict:
        if self.mode == "mock":
            return mock_data.MOCK_CONFIG_STATUS
        return self._unwrap_dict(self._request("GET", "/config/status"))

    def upload_run(self, uploaded_file) -> dict:
        if self.mode == "mock":
            return mock_data.create_uploaded_run(uploaded_file.name)
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type or "text/plain")}
        return self._unwrap_dict(self._request("POST", "/api/v1/runs/upload", files=files))

    def analyze_run(self, run_id: str) -> dict:
        if self.mode == "mock":
            return mock_data.analyze_run(run_id)
        return self._unwrap_dict(self._request("POST", f"/api/v1/runs/{run_id}/analyze"))

    def list_runs(self) -> list[dict]:
        if self.mode == "mock":
            return mock_data.list_runs()
        return self._unwrap_list(self._request("GET", "/api/v1/runs"), ("runs", "items", "data"))

    def get_run(self, run_id: str) -> dict:
        if self.mode == "mock":
            return mock_data.get_run(run_id)
        return self._unwrap_dict(self._request("GET", f"/api/v1/runs/{run_id}"), ("run", "data"))

    def get_incidents(self, run_id: str) -> list[dict]:
        if self.mode == "mock":
            return mock_data.get_incidents(run_id)
        return self._unwrap_list(
            self._request("GET", f"/api/v1/runs/{run_id}/incidents"),
            ("incidents", "items", "data"),
        )

    def get_cookbook(self, run_id: str) -> dict:
        if self.mode == "mock":
            return mock_data.get_cookbook(run_id)
        return self._unwrap_dict(self._request("GET", f"/api/v1/runs/{run_id}/cookbook"), ("cookbook", "data"))

    def get_timeline(self, run_id: str) -> list[dict]:
        if self.mode == "mock":
            return mock_data.get_timeline(run_id)
        return self._unwrap_list(
            self._request("GET", f"/api/v1/runs/{run_id}/timeline"),
            ("timeline", "events", "items", "data"),
        )

    def get_root_cause(self, run_id: str) -> dict | None:
        if self.mode == "mock":
            return mock_data.get_root_cause(run_id)
        payload = self._request("GET", f"/api/v1/runs/{run_id}/root-cause")
        if payload is None:
            return None
        return self._unwrap_dict(payload, ("root_cause", "data"))

    def get_artifacts(self, run_id: str) -> list[dict]:
        if self.mode == "mock":
            return mock_data.get_artifacts(run_id)
        return self._unwrap_list(
            self._request("GET", f"/api/v1/runs/{run_id}/artifacts"),
            ("artifacts", "items", "data"),
        )

    def export_json(self, run_id: str) -> dict:
        if self.mode == "mock":
            return mock_data.build_export_json(run_id)
        return self._unwrap_dict(self._request("GET", f"/api/v1/runs/{run_id}/export/json"), ("export", "data"))

    def export_markdown(self, run_id: str) -> str:
        if self.mode == "mock":
            return mock_data.build_export_markdown(run_id)
        return self._unwrap_text(self._request("GET", f"/api/v1/runs/{run_id}/export/markdown"))

    def test_llm(self) -> dict:
        if self.mode == "mock":
            return mock_data.MOCK_TEST_RESPONSES["llm"]
        return self._unwrap_dict(self._request("POST", "/api/v1/integrations/llm/test"))

    def test_slack(self) -> dict:
        if self.mode == "mock":
            return mock_data.MOCK_TEST_RESPONSES["slack"]
        return self._unwrap_dict(self._request("POST", "/api/v1/integrations/slack/test"))

    def test_jira(self) -> dict:
        if self.mode == "mock":
            return mock_data.MOCK_TEST_RESPONSES["jira"]
        return self._unwrap_dict(self._request("POST", "/api/v1/integrations/jira/test"))

    def analyze_sample(self) -> dict:
        if self.mode == "mock":
            uploaded = mock_data.create_uploaded_run("sample-demo.log")
            return mock_data.analyze_run(uploaded["run_id"])
        return self._unwrap_dict(self._request("POST", "/api/v1/demo/analyze-sample"))

    def get_workflow_mermaid(self) -> dict:
        if self.mode == "mock":
            return mock_data.get_workflow()
        return self._unwrap_dict(self._request("GET", "/api/v1/workflow/mermaid"), ("workflow", "data"))
