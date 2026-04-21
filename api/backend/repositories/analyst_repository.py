from backend.db_connection import load_query
from backend.repositories.base_repository import BaseRepository


class AnalystRepository(BaseRepository):
    def get_audit_log_summary(self):
        return self.fetch_all(load_query("analyst/get_audit_log_summary.sql"))

    def get_session_summary(self):
        return self.fetch_all(load_query("analyst/get_session_summary.sql"))

    def get_completed_chores(self):
        return self.fetch_all(load_query("analyst/get_completed_chores.sql"))

    def get_inactive_users(self):
        return self.fetch_all(load_query("analyst/get_inactive_users.sql"))

    def get_group_engagement(self):
        return self.fetch_all(load_query("analyst/get_group_engagement.sql"))

    def get_audit_log_activity(self):
        return self.fetch_all(load_query("analyst/get_audit_log_activity.sql"), {})
