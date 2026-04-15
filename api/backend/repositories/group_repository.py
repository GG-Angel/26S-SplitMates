from typing import Optional
from backend.db_connection import get_db, load_query
from backend.repositories.base_repository import BaseRepository


class GroupRepository(BaseRepository):
    def get_group(self, group_id: int):
        return self.fetch_one(
            load_query("groups/get_group.sql"), {"group_id": group_id}
        )

    def get_group_members(self, group_id: int):
        return self.fetch_all(
            load_query("groups/get_group_members.sql"), {"group_id": group_id}
        )

    def get_group_bills(self, group_id: int):
        return self.fetch_all(
            load_query("bills/get_group_bills.sql"), {"group_id": group_id}
        )

    def get_group_member_bills(
        self, group_id: int, user_id: int, unpaid_only: Optional[bool] = False
    ):
        return self.fetch_all(
            load_query("bills/get_group_member_bills.sql"),
            {"group_id": group_id, "user_id": user_id, "unpaid_only": unpaid_only},
        )

    def get_group_bill(self, group_id: int, bill_id: int):
        return self.fetch_one(
            load_query("bills/get_group_bill.sql"),
            {"group_id": group_id, "bill_id": bill_id},
        )

    def get_group_bill_assignees(self, group_id: int, bill_id: int):
        return self.fetch_all(
            load_query("bills/get_bill_assignees.sql"),
            {"group_id": group_id, "bill_id": bill_id},
        )

    def get_all_group_bill_assignees(self, group_id: int):
        return self.fetch_all(
            load_query("bills/get_group_bill_assignees.sql"),
            {"group_id": group_id},
        )

    def create_group(self, data: dict):
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                load_query("groups/insert_group.sql"),
                {
                    "group_leader": data["user_id"],
                    "name": data["name"],
                    "address": data["address"],
                    "city": data["city"],
                    "state": data["state"],
                    "zip_code": data["zip_code"],
                },
            )
            group_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO group_members (user_id, group_id) VALUES (%s, %s)",
                (data["user_id"], group_id),
            )
            conn.commit()

    def create_bill(self, data: dict):
        with get_db() as conn:
            # insert bill first
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                load_query("bills/insert_bill.sql"),
                {
                    "group_id": data["group_id"],
                    "created_by": data["user_id"],
                    "total_cost": data["total_cost"],
                    "title": data["title"],
                    "due_at": data["due_at"],
                },
            )
            # then add the assignments
            bill_id = cursor.lastrowid
            for assignee in data["assignees"]:
                cursor.execute(
                    load_query("bills/insert_bill_assignment.sql"),
                    {
                        "bill_id": bill_id,
                        "user_id": assignee["user_id"],
                        "split_percentage": assignee["split_percentage"],
                    },
                )
            conn.commit()

    def delete_bill(self, bill_id: int):
        self.execute(load_query("bills/delete_bill.sql"), {"bill_id": bill_id})

    def get_group_chores(self, group_id: int, incomplete_only: Optional[bool] = False):
        return self.fetch_all(
            load_query("chores/get_group_chores.sql"),
            {"group_id": group_id, "incomplete_only": incomplete_only},
        )

    def get_group_chore_leaderboard(self, group_id: int):
        return self.fetch_all(
            load_query("chores/get_group_chore_leaderboard.sql"), {"group_id": group_id}
        )

    def get_chore_assignees(self, chore_id: int):
        return self.fetch_all(
            load_query("chores/get_chore_assignees.sql"), {"chore_id": chore_id}
        )

    def assign_user_to_chore(self, chore_id: int, user_id: int):
        self.execute(
            load_query("chores/insert_chore_assignment.sql"),
            {"chore_id": chore_id, "user_id": user_id},
        )

    def unassign_user_from_chore(self, chore_id: int, user_id: int):
        self.execute(
            load_query("chores/delete_chore_assignment.sql"),
            {"chore_id": chore_id, "user_id": user_id},
        )

    def create_chore(self, group_id: int, data: dict):
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                load_query("chores/insert_chore.sql"),
                {
                    "group_id": group_id,
                    "created_by": data["user_id"],
                    "title": data["title"],
                    "effort": data["effort"],
                    "due_at": data.get("due_at"),
                },
            )
            chore_id = cursor.lastrowid
            for user_id in data.get("assignees", []):
                cursor.execute(
                    load_query("chores/insert_chore_assignment.sql"),
                    {"chore_id": chore_id, "user_id": user_id},
                )
            conn.commit()

    def complete_chore(self, chore_id: int):
        self.execute(load_query("chores/complete_chore.sql"), {"chore_id": chore_id})

    def update_chore(self, chore_id: int, data: dict):
        self.execute(
            load_query("chores/update_chore.sql"),
            {
                "chore_id": chore_id,
                "title": data["title"],
                "effort": data["effort"],
                "due_at": data.get("due_at"),
            },
        )

    def delete_chore(self, chore_id: int):
        self.execute(load_query("chores/delete_chore.sql"), {"chore_id": chore_id})

    def get_group_events(self, group_id: int):
        return self.fetch_all(
            load_query("events/get_group_events.sql"), {"group_id": group_id}
        )

    def create_event(self, group_id: int, data: dict):
        self.execute(
            load_query("events/insert_event.sql"),
            {
                "group_id": group_id,
                "created_by": data["user_id"],
                "title": data["title"],
                "starts_at": data["starts_at"],
                "ends_at": data["ends_at"],
                "is_private": data["is_private"],
            },
        )

    def get_group_invites(self, group_id: int, pending_only: bool = False):
        return self.fetch_all(
            load_query("invitations/get_group_invites.sql"),
            {"group_id": group_id, "pending_only": pending_only},
        )

    def get_user_by_email(self, email: str):
        return self.fetch_one(
            load_query("users/get_user_by_email.sql"), {"email": email}
        )

    def get_pending_invite(self, group_id: int, user_id: int):
        return self.fetch_one(
            load_query("invitations/get_pending_invite.sql"),
            {"group_id": group_id, "user_id": user_id},
        )

    def is_group_member(self, group_id: int, user_id: int):
        return self.fetch_one(
            load_query("groups/is_group_member.sql"),
            {"group_id": group_id, "user_id": user_id},
        )

    def create_invitation(self, group_id: int, data: dict):
        self.execute(
            load_query("invitations/insert_invitation.sql"),
            {"group_id": group_id, "sent_to": data["sent_to"]},
        )

    def delete_invitation(self, invitation_id: int):
        self.execute(
            load_query("invitations/delete_invitation.sql"),
            {"invitation_id": invitation_id},
        )

    def transfer_group_ownership(self, group_id: int, user_id: int):
        self.execute(
            load_query("groups/transfer_group_ownership.sql"),
            {"group_id": group_id, "user_id": user_id},
        )

    def delete_group(self, group_id: int):
        self.execute(load_query("groups/delete_group.sql"), {"group_id": group_id})

    def remove_group_member(self, group_id: int, user_id: int):
        self.execute_script(
            load_query("groups/remove_group_member.sql"),
            {"group_id": group_id, "user_id": user_id},
        )

    def rename_group(self, group_id: int, name: str):
        self.execute(
            load_query("groups/rename_group.sql"),
            {"group_id": group_id, "name": name},
        )

    def get_user_groups_led(self, user_id: int):
        return self.fetch_all(
            load_query("groups/get_user_groups_led.sql"),
            {"user_id": user_id},
        )
