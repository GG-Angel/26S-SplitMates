from typing import List, Optional
from backend.db_connection import load_query
from backend.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    def get_user(self, user_id: int):
        return self.fetch_one(load_query("users/get_user.sql"), {"user_id": user_id})

    def delete_user(self, user_id: int):
        self.execute(load_query("users/delete_user.sql"), {"user_id": user_id})

    def insert_user(self, user: dict) -> None:
        self.execute(load_query("users/insert_user.sql"), user)

    def insert_users(self, users: List[dict]) -> None:
        self.execute_many(load_query("users/insert_user.sql"), users)

    def get_user_groups(self, user_id: int):
        return self.fetch_all(
            load_query("groups/get_user_groups.sql"), {"user_id": user_id}
        )

    def get_user_chores(self, user_id: int, group_id: Optional[int] = None):
        return self.fetch_all(
            load_query("chores/get_user_chores.sql"),
            {"user_id": user_id, "group_id": group_id},
        )

    def get_user_invitations(self, user_id: int, pending_only: bool = False):
        return self.fetch_all(
            load_query("invitations/get_user_invitations.sql"),
            {"user_id": user_id, "pending_only": pending_only},
        )

    def accept_invitation(self, invitation_id: int, user_id: int):
        self.execute_script(
            load_query("invitations/accept_invitation.sql"),
            {"invitation_id": invitation_id, "user_id": user_id},
        )

    def delete_invitation(self, invitation_id: int):
        self.execute(
            load_query("invitations/delete_invitation.sql"),
            {"invitation_id": invitation_id},
        )

    def pay_bill(self, user_id: int, bill_id: int):
        self.execute(
            load_query("bills/pay_bill.sql"),
            {"bill_id": bill_id, "user_id": user_id},
        )

    def rename_user(self, user_id: int, new_first_name: str, new_last_name: str):
        self.execute(
            load_query("users/rename_user.sql"),
            {
                "user_id": user_id,
                "first_name": new_first_name,
                "last_name": new_last_name,
            },
        )
