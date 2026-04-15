from typing import List
from backend.db_connection import load_query
from backend.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    def get_user(self, user_id: int):
        return self.fetch_one(load_query("users/get_user.sql"), {"user_id": user_id})

    def insert_user(self, user: dict) -> None:
        self.execute(load_query("users/insert_user.sql"), user)

    def insert_users(self, users: List[dict]) -> None:
        self.execute_many(load_query("users/insert_user.sql"), users)

    def get_user_groups(self, user_id: int):
        return self.fetch_all(
            load_query("groups/get_user_groups.sql"), {"user_id": user_id}
        )

    def get_user_chores(self, user_id: int, group_id: int = None):
        return self.fetch_all(
            load_query("chores/get_user_chores.sql"),
            {"user_id": user_id, "group_id": group_id},
        )

    def get_user_invitations(self, user_id: int, pending_only: bool = False):
        return self.fetch_all(
            load_query("invitations/get_user_invitations.sql"),
            {"user_id": user_id, "pending_only": pending_only},
        )

    def pay_bill(self, user_id: int, bill_id: int):
        self.execute(
            load_query("bills/pay_bill.sql"),
            {"bill_id": bill_id, "user_id": user_id},
        )
