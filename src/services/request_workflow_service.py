import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

class RequestWorkflowService:
    def __init__(
            self,
            db_path: str | Path,
            approver_ids: set[int] | None = None,
    ) -> None:
        self.db_path = Path(db_path)
        self.approver_ids = frozenset(approver_ids or set())

        if not self.db_path.is_file():
            raise FileNotFoundError(
                f"SQLite DBが見つかりません: {self.db_path}"
            )

        self._initialize_database()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        )

    def _initialize_database(self) -> None:
        with closing(self._connect()) as conn:
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS request_status_history (
                        history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        request_id INTEGER NOT NULL,
                        from_status TEXT NOT NULL,
                        to_status TEXT NOT NULL,
                        action TEXT NOT NULL,
                        actor_id TEXT NOT NULL,
                        reason TEXT,
                        changed_at TEXT NOT NULL
                    )
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS
                    idx_request_status_history_request
                    ON request_status_history(request_id)
                """)

    def is_approver(self, user_id: int) -> bool:
        return user_id in self.approver_ids

    def request_approval(
            self,
            *,
            request_id: int,
            requester_id: int,
    ) -> bool:
        """本人の分類済みGoogle依頼を承認待ちにする。"""

        with closing(self._connect()) as conn:
            with conn:
                cursor = conn.execute(
                    """
                    UPDATE requests
                    SET status = 'needs_approval',
                        approval_status = 'pending'
                    WHERE request_id = ?
                      AND requester_id = ?
                      AND status = 'classified'
                      AND classification_category = 'google_candidate'
                    """,
                    (request_id, str(requester_id)),
                )

                if cursor.rowcount != 1:
                    return False

                conn.execute(
                    """
                    INSERT INTO request_status_history(
                        request_id,
                        from_status,
                        to_status,
                        action,
                        actor_id,
                        reason,
                        changed_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        request_id,
                        "classified",
                        "needs_approval",
                        "approval_requested",
                        str(requester_id),
                        None,
                        self._now(),
                    ),
                )

                return True

    def get_for_review(
            self,
            *,
            request_id: int,
            approver_id: int,
    ) -> dict | None:
        """承認担当者だけが依頼の内容を閲覧できる。"""

        if not self.is_approver(approver_id):
            raise PermissionError("承認担当者ではありません。")

        with closing(self._connect()) as conn:
            row = conn.execute(
                """
                SELECT
                    request_id,
                    requester_id,
                    request_text,
                    status,
                    classification_category,
                    target_service,
                    classification_reason,
                    approval_status
                FROM requests
                WHERE request_id = ?
                """,
                (request_id,),
            ).fetchone()

            return dict(row) if row is not None else None

    def decide(
            self,
            *,
            request_id: int,
            approver_id: int,
            decision: str,
            reason: str = "",
    ) -> bool:
        """管理者による承認・却下を記録する。"""

        if not self.is_approver(approver_id):
            raise PermissionError("承認担当者ではありません。")

        if decision not in ("approve", "reject"):
            raise ValueError("decisionはapproveまたはrejectです。")

        reason = reason.strip()

        if decision == "reject" and not reason:
            raise ValueError("却下する場合は理由が必要です。")

        if len(reason) > 1000:
            raise ValueError("理由は1000文字以内で指定してください。")

        new_status = (
            "approved" if decision == "approve"
            else "rejected"
        )

        with closing(self._connect()) as conn:
            with conn:
                cursor = conn.execute(
                    """
                    UPDATE requests
                    SET status = ?,
                        approval_status = ?
                    WHERE request_id = ?
                      AND status = 'needs_approval'
                      AND approval_status = 'pending'
                      AND classification_category = 'google_candidate'
                    """,
                    (
                        new_status,
                        new_status,
                        request_id,
                    ),
                )

                if cursor.rowcount != 1:
                    return False

                conn.execute(
                    """
                    INSERT INTO request_status_history (
                        request_id,
                        from_status,
                        to_status,
                        action,
                        actor_id,
                        reason,
                        changed_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        request_id,
                        "needs_approval",
                        new_status,
                        decision,
                        str(approver_id),
                        reason or None,
                        self._now(),
                    ),
                )

                return True