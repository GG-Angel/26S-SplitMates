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

    def get_user_bills(self, user_id: int):
        return self.fetch_all(load_query("bills/get_user_bills.sql"), {"user_id": user_id})

    def get_user_chores(self, user_id: int):
        return self.fetch_all(load_query("chores/get_user_chores.sql"), {"user_id": user_id})
