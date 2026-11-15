
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from services.request_classifier import Classification


DB_PATH = Path(__file__).resolve().parents[2] / "data" / "coreworld.db"


class RequestService:
    NEW_COLUMNS = {
        "classification_category": "TEXT",
        "target_service": "TEXT",
        "classification_reason": "TEXT",
        "approval_status": "TEXT",
        "classified_at": "TEXT",
    }

    STATUS_MAP = {
        "google_candidate": "classified",
        "manual_required": "manual_required",
        "needs_clarification": "needs_clarification",
    }

    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = Path(db_path) if db_path is not None else DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_database(self) -> None:
        with closing(self._connect()) as conn:
            with conn:
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

                existing_columns = {
                    row["name"]
                    for row in conn.execute("PRAGMA table_info(requests)")
                }

                for name, column_type in self.NEW_COLUMNS.items():
                    if name not in existing_columns:
                        conn.execute(
                            f"ALTER TABLE requests "
                            f"ADD COLUMN {name} {column_type}"
                        )

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

        with closing(self._connect()) as conn:
            with conn:
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
                return cursor.lastrowid

    def get_request(
        self,
        *,
        request_id: int,
        requester_id: int,
    ) -> dict | None:
        with closing(self._connect()) as conn:
            row = conn.execute(
                """
                SELECT
                    request_id,
                    requester_id,
                    request_text,
                    status,
                    source_type,
                    created_at,
                    classification_category,
                    target_service,
                    classification_reason,
                    approval_status,
                    classified_at
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
        if not 1 <= limit <= 20:
            raise ValueError("取得件数は1～20で指定してください。")

        with closing(self._connect()) as conn:
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

    def save_classification(
        self,
        *,
        request_id: int,
        requester_id: int,
        classification: Classification,
    ) -> bool:
        if classification.category not in self.STATUS_MAP:
            raise ValueError("未対応の分類カテゴリです。")

        new_status = self.STATUS_MAP[classification.category]

        approval_status = (
            "required"
            if classification.requires_approval
            else "undetermined"
        )

        classified_at = datetime.now(
            timezone.utc
        ).isoformat(timespec="seconds")

        with closing(self._connect()) as conn:
            with conn:
                cursor = conn.execute(
                    """
                    UPDATE requests
                    SET
                        status = ?,
                        classification_category = ?,
                        target_service = ?,
                        classification_reason = ?,
                        approval_status = ?,
                        classified_at = ?
                    WHERE request_id = ?
                      AND requester_id = ?
                      AND status = 'received'
                      AND classification_category IS NULL
                    """,
                    (
                        new_status,
                        classification.category,
                        classification.target_service,
                        classification.reason,
                        approval_status,
                        classified_at,
                        request_id,
                        str(requester_id),
                    ),
                )

                return cursor.rowcount == 1
