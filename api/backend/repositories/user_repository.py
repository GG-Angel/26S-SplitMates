from typing import List
from backend.db_connection import load_query
from backend.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    def insert_user(self, user: dict) -> None:
        self.execute(load_query("users/insert_user.sql"), user)

    def insert_users(self, users: List[dict]) -> None:
        self.execute_many(load_query("users/insert_user.sql"), users)
