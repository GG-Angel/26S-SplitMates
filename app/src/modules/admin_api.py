import os
from typing import Any

import requests


API_BASE = os.getenv("ADMIN_API_BASE", "http://web-api:4000/admin")
REQUEST_TIMEOUT = 10

# TODO: use api/client.py to interact with the api


def _url(path: str) -> str:
    return f"{API_BASE.rstrip('/')}/{path.lstrip('/')}"


def _get(path: str, params: dict[str, Any] | None = None) -> Any:
    response = requests.get(_url(path), params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


def _request(method: str, path: str, payload: dict | None = None) -> Any:
    response = requests.request(method, _url(path), json=payload, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    if response.status_code == 204:
        return None
    return response.json()


def get_admin_summary() -> dict[str, Any]:
    return _get("summary")


def get_admin_users() -> list[dict[str, Any]]:
    return _get("users")


def get_admin_groups() -> list[dict[str, Any]]:
    return _get("groups")


def get_admin_group(group_id: int) -> dict[str, Any]:
    return _get(f"groups/{group_id}")


def delete_admin_group(group_id: int) -> Any:
    response = requests.delete(_url(f"groups/{group_id}"), timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


def get_support_tickets() -> list[dict[str, Any]]:
    return _get("support_tickets")


def get_support_ticket(ticket_id: int) -> dict[str, Any]:
    return _get(f"support_tickets/{ticket_id}")


def update_support_ticket(ticket_id: int, payload: dict[str, Any]) -> Any:
    return _request("PUT", f"support_tickets/{ticket_id}", payload)


def get_user_reports() -> list[dict[str, Any]]:
    return _get("user_reports")


def get_user_report(report_id: int) -> dict[str, Any]:
    return _get(f"user_reports/{report_id}")


def update_user_report(report_id: int, payload: dict[str, Any]) -> Any:
    return _request("PUT", f"user_reports/{report_id}", payload)


def get_app_versions() -> list[dict[str, Any]]:
    return _get("app_versions")


def create_app_version(payload: dict[str, Any]) -> Any:
    return _request("POST", "app_versions", payload)


def get_user_bans(user_id: int) -> list[dict[str, Any]]:
    return _get(f"users/{user_id}/bans")


def issue_user_ban(user_id: int, payload: dict[str, Any]) -> Any:
    return _request("POST", f"users/{user_id}/bans", payload)


def update_user_ban(user_id: int, ban_id: int, payload: dict[str, Any]) -> Any:
    return _request("PUT", f"users/{user_id}/bans/{ban_id}", payload)


def lift_user_ban(user_id: int, ban_id: int) -> Any:
    return _request("DELETE", f"users/{user_id}/bans/{ban_id}")


def get_audit_logs(user_id: int | None = None, action_type: str | None = None) -> list[dict[str, Any]]:
    params: dict[str, Any] = {}
    if user_id is not None:
        params["user_id"] = user_id
    if action_type:
        params["action_type"] = action_type
    return _get("audit_logs", params=params)
