import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "date" / "coreworld.db"

class RequestService:
    def __init__(self) -> None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

    def _initialize_database(self) -> None:
        with closing(sqlite3.connect(DB_PATH)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS requests (
                    request_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_type TEXT NOT NULL,
                    source_guild_id TEXT,
                    source_channel_id TEXT NOT NULL,
                    source_message_id TEXT,
                    requester_id TEXT NOT NULL,
                    request_text TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'received',
                    created_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def create_request(
            self,
            *,
            requester_id: int,
            source_channel_id: int,
            source_guild_id: int | None,
            request_text: str,
    ) -> int:
        
        content = request_text.strip()

        if not content:
            raise ValueError("依頼内容が空です。")

        created_at = datetime.now(
            timezone.utc
        ).isoformat(timespec="seconds")

        with closing(sqlite3.connect(DB_PATH)) as conn:
            cursor = conn.execute(
                """
                INSERT INTO requests (
                    source_type,
                    source_guild_id,
                    source_channel_id,
                    requester_id,
                    request_text,
                    status,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "slash",
                    str(source_guild_id) if source_guild_id else None,
                    str(source_channel_id),
                    str(requester_id),
                    content,
                    "received",
                    created_at,
                ),
            )

            conn.commit()
            return cursor.lastrowid