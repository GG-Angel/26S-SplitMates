import os
from typing import Any

from api.client import APIClient


ADMIN_API_BASE = os.getenv("ADMIN_API_BASE", "http://web-api:4000/admin")
_client = APIClient(base_url=ADMIN_API_BASE)


def get_admin_summary() -> dict[str, Any]:
    return _client.get("summary")


def get_admin_users() -> list[dict[str, Any]]:
    return _client.get("users")


def get_admin_groups() -> list[dict[str, Any]]:
    return _client.get("groups")


def get_admin_group(group_id: int) -> dict[str, Any]:
    return _client.get(f"groups/{group_id}")


def delete_admin_group(group_id: int) -> Any:
    return _client.delete(f"groups/{group_id}")


def get_support_tickets() -> list[dict[str, Any]]:
    return _client.get("support_tickets")


def get_support_ticket(ticket_id: int) -> dict[str, Any]:
    return _client.get(f"support_tickets/{ticket_id}")


def update_support_ticket(ticket_id: int, payload: dict[str, Any]) -> Any:
    return _client.put(f"support_tickets/{ticket_id}", json=payload)


def get_user_reports() -> list[dict[str, Any]]:
    return _client.get("user_reports")


def get_user_report(report_id: int) -> dict[str, Any]:
    return _client.get(f"user_reports/{report_id}")


def update_user_report(report_id: int, payload: dict[str, Any]) -> Any:
    return _client.put(f"user_reports/{report_id}", json=payload)


def get_app_versions() -> list[dict[str, Any]]:
    return _client.get("app_versions")


def create_app_version(payload: dict[str, Any]) -> Any:
    return _client.post("app_versions", json=payload)


def get_user_bans(user_id: int) -> list[dict[str, Any]]:
    return _client.get(f"users/{user_id}/bans")


def issue_user_ban(user_id: int, payload: dict[str, Any]) -> Any:
    return _client.post(f"users/{user_id}/bans", json=payload)


def update_user_ban(user_id: int, ban_id: int, payload: dict[str, Any]) -> Any:
    return _client.put(f"users/{user_id}/bans/{ban_id}", json=payload)


def lift_user_ban(user_id: int, ban_id: int) -> Any:
    return _client.delete(f"users/{user_id}/bans/{ban_id}")


def get_audit_logs(user_id: int | None = None, action_type: str | None = None) -> list[dict[str, Any]]:
    params: dict[str, Any] = {}
    if user_id is not None:
        params["user_id"] = user_id
    if action_type:
        params["action_type"] = action_type
    return _client.get("audit_logs", params=params)
