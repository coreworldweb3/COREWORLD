
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path


# SQLiteの正式な保存先
DB_PATH = Path(__file__).resolve().parents[2] / "data" / "coreworld.db"


class RequestService:
    def __init__(self) -> None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

    def _initialize_database(self) -> None:
        with closing(sqlite3.connect(DB_PATH)) as conn:
            conn.execute(
                """
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
                """
            )
            conn.commit()

    def create_request(
        self,
        *,
        requester_id: int,
        source_channel_id: int,
        source_guild_id: int | None,
        request_text: str,
    ) -> int:
        """新しい依頼をSQLiteに保存する。"""

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
                    str(source_guild_id)
                    if source_guild_id is not None else None,
                    str(source_channel_id),
                    str(requester_id),
                    content,
                    "received",
                    created_at,
                ),
            )

            conn.commit()
            return cursor.lastrowid

    def get_request(
        self,
        *,
        request_id: int,
        requester_id: int,
    ) -> dict | None:
        """受付番号から本人の依頼を取得する。"""

        with closing(sqlite3.connect(DB_PATH)) as conn:
            conn.row_factory = sqlite3.Row

            row = conn.execute(
                """
                SELECT
                    request_id,
                    requester_id,
                    request_text,
                    status,
                    source_type,
                    created_at
                FROM requests
                WHERE request_id = ?
                  AND requester_id = ?
                """,
                (request_id, str(requester_id)),
            ).fetchone()

            return dict(row) if row is not None else None

    def list_requests(
        self,
        *,
        requester_id: int,
        limit: int = 10,
    ) -> list[dict]:
        """本人の依頼を新しい順に一覧取得する。"""

        if not 1 <= limit <= 20:
            raise ValueError(
                "取得件数は1～20で指定してください。"
            )

        with closing(sqlite3.connect(DB_PATH)) as conn:
            conn.row_factory = sqlite3.Row

            rows = conn.execute(
                """
                SELECT
                    request_id,
                    request_text,
                    status,
                    created_at
                FROM requests
                WHERE requester_id = ?
                ORDER BY request_id DESC
                LIMIT ?
                """,
                (str(requester_id), limit),
            ).fetchall()

            return [dict(row) for row in rows]
