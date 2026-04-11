from backend.db_connection import load_query
from backend.repositories.base_repository import BaseRepository


class GroupRepository(BaseRepository):
    def get_group(self, group_id: int):
        return self.fetch_one(
            load_query("groups/get_group.sql"), {"group_id": group_id}
        )
