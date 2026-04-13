from typing import Optional, Any, Dict, List, cast
from backend.db_connection import get_db


class BaseRepository:
    def fetch_one(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        if params is not None:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cast(Optional[Dict[str, Any]], cursor.fetchone())

    def fetch_all(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        if params is not None:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cast(List[Dict[str, Any]], cursor.fetchall())

    def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> None:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        if params is not None:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()

    def execute_many(self, query: str, params: List[Dict[str, Any]]) -> None:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.executemany(query, params)
        conn.commit()
