from backend.db_connection import load_query
from backend.repositories.base_repository import BaseRepository


class GroupRepository(BaseRepository):
    def get_group(self, group_id: int):
        return self.fetch_one(
            load_query("groups/get_group.sql"), {"group_id": group_id}
        )

    def get_group_bills(self, group_id: int):
        return self.fetch_all(
            load_query("bills/get_group_bills.sql"), {"group_id": group_id}
        )

    def get_group_bill(self, group_id: int, bill_id: int):
        return self.fetch_one(
            load_query("bills/get_group_bill.sql"),
            {"group_id": group_id, "bill_id": bill_id},
        )

    def create_group(self, data: dict):
        self.execute(
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
