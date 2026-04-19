from typing import Any, Optional

from ..db_connection import get_db, load_query
from .base_repository import BaseRepository


class AdminRepository(BaseRepository):
    def get_summary_total_users(self):
        return self.fetch_one(load_query("admin/get_summary_total_users.sql"))

    def get_summary_active_households(self):
        return self.fetch_one(load_query("admin/get_summary_active_households.sql"))

    def get_summary_open_tickets(self):
        return self.fetch_one(load_query("admin/get_summary_open_tickets.sql"))

    def get_summary_inactive_users(self):
        return self.fetch_one(load_query("admin/get_summary_inactive_users.sql"))

    def get_summary_urgent_tickets(self):
        return self.fetch_one(load_query("admin/get_summary_urgent_tickets.sql"))

    def get_summary_recent_tickets(self):
        return self.fetch_all(load_query("admin/get_summary_recent_tickets.sql"))

    def get_summary_recent_activity(self):
        return self.fetch_all(load_query("admin/get_summary_recent_activity.sql"))

    def get_all_users(self):
        return self.fetch_all(load_query("admin/get_all_users.sql"))

    def get_groups_for_user(self, user_id: int):
        return self.fetch_all(
            load_query("admin/get_groups_for_user.sql"), {"user_id": user_id}
        )

    def get_all_groups(self):
        return self.fetch_all(load_query("admin/get_all_groups.sql"))

    def get_group_by_id(self, group_id: int):
        return self.fetch_one(
            load_query("admin/get_group_by_id.sql"), {"group_id": group_id}
        )

    def delete_group_by_id(self, group_id: int):
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                load_query("admin/delete_group_by_id.sql"), {"group_id": group_id}
            )
            if cursor.rowcount == 0:
                conn.rollback()
                return False
            conn.commit()
            return True

    def get_bans_for_user(self, user_id: int):
        return self.fetch_all(
            load_query("admin/get_bans_for_user.sql"), {"user_id": user_id}
        )

    def insert_ban_for_user(self, user_id: int, data: dict):
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                load_query("admin/insert_ban_for_user.sql"),
                {
                    "user_id": user_id,
                    "issued_by": data.get("issued_by"),
                    "reasons": data.get("reasons"),
                    "expires_at": data.get("expires_at"),
                },
            )
            ban_id = cursor.lastrowid
            cursor.execute(
                load_query("admin/set_user_status_suspended.sql"),
                {"user_id": user_id},
            )
            conn.commit()
            return ban_id

    def update_ban_for_user(self, user_id: int, ban_id: int, data: dict):
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                load_query("admin/update_ban_for_user.sql"),
                {
                    "user_id": user_id,
                    "ban_id": ban_id,
                    "reasons": data.get("reasons"),
                    "expires_at": data.get("expires_at"),
                },
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete_ban_for_user(self, user_id: int, ban_id: int):
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                load_query("admin/delete_ban_for_user.sql"),
                {"user_id": user_id, "ban_id": ban_id},
            )
            if cursor.rowcount == 0:
                conn.rollback()
                return False

            cursor.execute(
                load_query("admin/count_active_bans_for_user.sql"),
                {"user_id": user_id},
            )
            row = cursor.fetchone()
            active_bans = row["active_bans"] if row else 0
            if active_bans == 0:
                cursor.execute(
                    load_query("admin/set_user_status_active.sql"),
                    {"user_id": user_id},
                )

            conn.commit()
            return True

    def get_all_support_tickets(self):
        return self.fetch_all(load_query("admin/get_all_support_tickets.sql"))

    def get_support_ticket_by_id(self, ticket_id: int):
        return self.fetch_one(
            load_query("admin/get_support_ticket_by_id.sql"), {"ticket_id": ticket_id}
        )

    def update_support_ticket(self, ticket_id: int, data: dict):
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                load_query("admin/update_support_ticket.sql"),
                {
                    "ticket_id": ticket_id,
                    "status": data.get("status"),
                    "priority": data.get("priority"),
                    "description": data.get("description"),
                    "assigned_to": data.get("assigned_to"),
                    "title": data.get("title"),
                    "resolved_at": data.get("resolved_at"),
                },
            )
            conn.commit()
            return cursor.rowcount > 0

    def get_support_tickets_by_submitter(self, user_id: int):
        return self.fetch_all(
            load_query("admin/get_support_tickets_by_submitter.sql"),
            {"user_id": user_id},
        )

    def insert_user_report(self, reported_user: int, reported_by: int, reason: str):
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                load_query("admin/insert_user_report.sql"),
                {"reported_user": reported_user, "reported_by": reported_by, "reason": reason},
            )
            report_id = cursor.lastrowid
            conn.commit()
            return report_id

    def get_all_user_reports(self):
        return self.fetch_all(load_query("admin/get_all_user_reports.sql"))

    def get_user_reports_by_reporter(self, reported_by: int):
        return self.fetch_all(
            load_query("admin/get_user_reports_by_reporter.sql"),
            {"reported_by": reported_by},
        )

    def get_user_reports_against_user(self, reported_user: int):
        return self.fetch_all(
            load_query("admin/get_user_reports_against_user.sql"),
            {"reported_user": reported_user},
        )

    def get_user_report_by_id(self, report_id: int):
        return self.fetch_one(
            load_query("admin/get_user_report_by_id.sql"), {"report_id": report_id}
        )

    def update_user_report(self, report_id: int, data: dict):
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                load_query("admin/update_user_report.sql"),
                {
                    "report_id": report_id,
                    "status": data.get("status"),
                    "reviewed_by": data.get("reviewed_by"),
                    "reviewed_at": data.get("reviewed_at"),
                },
            )
            conn.commit()
            return cursor.rowcount > 0

    def get_all_app_versions(self):
        return self.fetch_all(load_query("admin/get_all_app_versions.sql"))

    def create_app_version(self, data: dict):
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                load_query("admin/insert_app_version.sql"),
                {
                    "version_number": data.get("version_number"),
                    "deployed_by": data.get("deployed_by"),
                    "status": data.get("status", "deployed"),
                    "release_notes": data.get("release_notes"),
                    "deployed_at": data.get("deployed_at"),
                },
            )
            conn.commit()
            return cursor.lastrowid

    def get_audit_logs(
        self, user_id: Optional[int] = None, action_type: Optional[str] = None
    ):
        return self.fetch_all(
            load_query("admin/get_audit_logs.sql"),
            {"user_id": user_id, "action_type": action_type},
        )

    def maintenance_check(self):
        checks: dict[str, Any] = {}

        checks["users_count"] = (self.fetch_one(load_query("admin/maintenance_count_users.sql")) or {}).get("c", 0)
        checks["groups_count"] = (self.fetch_one(load_query("admin/maintenance_count_groups.sql")) or {}).get("c", 0)
        checks["bills_count"] = (self.fetch_one(load_query("admin/maintenance_count_bills.sql")) or {}).get("c", 0)
        checks["group_members_count"] = (self.fetch_one(load_query("admin/maintenance_count_group_members.sql")) or {}).get("c", 0)
        checks["orphan_bills"] = (self.fetch_one(load_query("admin/maintenance_count_orphan_bills.sql")) or {}).get("c", 0)
        checks["orphan_bill_assignments"] = (self.fetch_one(load_query("admin/maintenance_count_orphan_bill_assignments.sql")) or {}).get("c", 0)

        checks["status"] = (
            "ok"
            if checks["orphan_bills"] == 0 and checks["orphan_bill_assignments"] == 0
            else "warning"
        )
        return checks
