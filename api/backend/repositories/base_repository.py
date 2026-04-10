from typing import Optional, Any, Dict, List
from backend.db_connection import get_db


class BaseRepository:
    def fetch_one(self, query: str, params: Optional[Dict[str, Any]] = None):
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            if params is not None:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchone()

    def fetch_all(self, query: str, params: Optional[Dict[str, Any]] = None):
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            if params is not None:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()

    def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> None:
        with get_db() as conn:
            cursor = conn.cursor()
            if params is not None:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()

    def execute_many(self, query: str, params: List[Dict[str, Any]]) -> None:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params)
            conn.commit()
