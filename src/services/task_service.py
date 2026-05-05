from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import sqlite3
from typing import List, Optional


@dataclass
class TaskInfo:
    task_id: int
    channel_id: int
    created_by: int
    title: str
    description: str
    assignee: Optional[str]
    priority: str
    status: str
    created_at: datetime


class TaskService:
    """SQLiteでタスク情報を管理するサービス。"""

    VALID_PRIORITIES = {"low", "middle", "high"}
    VALID_STATUSES = {"todo", "doing", "waiting", "done", "archived"}

    def __init__(self, db_path: str = "data/coreworld.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

    def add_task(
        self,
        channel_id: int,
        created_by: int,
        title: str,
        description: str = "",
        assignee: Optional[str] = None,
        priority: str = "middle",
    ) -> TaskInfo:
        normalized_priority = self._normalize_priority(priority)
        created_at = datetime.now()

        with self._get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO tasks (
                    channel_id,
                    created_by,
                    title,
                    description,
                    assignee,
                    priority,
                    status,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    channel_id,
                    created_by,
                    title.strip(),
                    description.strip(),
                    assignee.strip() if assignee else None,
                    normalized_priority,
                    "todo",
                    created_at.isoformat(),
                ),
            )
            task_id = cursor.lastrowid

        return TaskInfo(
            task_id=task_id,
            channel_id=channel_id,
            created_by=created_by,
            title=title.strip(),
            description=description.strip(),
            assignee=assignee.strip() if assignee else None,
            priority=normalized_priority,
            status="todo",
            created_at=created_at,
        )

    def list_tasks(self, channel_id: int) -> List[TaskInfo]:
        with self._get_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    task_id,
                    channel_id,
                    created_by,
                    title,
                    description,
                    assignee,
                    priority,
                    status,
                    created_at
                FROM tasks
                WHERE channel_id = ?
                ORDER BY task_id ASC
                """,
                (channel_id,),
            ).fetchall()

        return [self._row_to_task(row) for row in rows]

    def find_task(self, channel_id: int, task_id: int) -> Optional[TaskInfo]:
        with self._get_connection() as connection:
            row = connection.execute(
                """
                SELECT
                    task_id,
                    channel_id,
                    created_by,
                    title,
                    description,
                    assignee,
                    priority,
                    status,
                    created_at
                FROM tasks
                WHERE channel_id = ? AND task_id = ?
                """,
                (channel_id, task_id),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_task(row)

    def mark_done(self, channel_id: int, task_id: int) -> Optional[TaskInfo]:
        return self.move_task(channel_id, task_id, "done")

    def move_task(
        self,
        channel_id: int,
        task_id: int,
        new_status: str,
    ) -> Optional[TaskInfo]:
        normalized_status = self._normalize_status(new_status)

        with self._get_connection() as connection:
            cursor = connection.execute(
                """
                UPDATE tasks
                SET status = ?
                WHERE channel_id = ? AND task_id = ?
                """,
                (normalized_status, channel_id, task_id),
            )

            if cursor.rowcount == 0:
                return None

        return self.find_task(channel_id, task_id)

    def delete_task(self, channel_id: int, task_id: int) -> Optional[TaskInfo]:
        task = self.find_task(channel_id, task_id)
        if task is None:
            return None

        with self._get_connection() as connection:
            connection.execute(
                """
                DELETE FROM tasks
                WHERE channel_id = ? AND task_id = ?
                """,
                (channel_id, task_id),
            )

        return task

    def _initialize_database(self) -> None:
        with self._get_connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id INTEGER NOT NULL,
                    created_by INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    assignee TEXT,
                    priority TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def _get_connection(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _row_to_task(self, row: sqlite3.Row) -> TaskInfo:
        return TaskInfo(
            task_id=row["task_id"],
            channel_id=row["channel_id"],
            created_by=row["created_by"],
            title=row["title"],
            description=row["description"],
            assignee=row["assignee"],
            priority=row["priority"],
            status=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def _normalize_priority(self, priority: str) -> str:
        value = priority.strip().lower()

        if value in self.VALID_PRIORITIES:
            return value

        return "middle"

    def _normalize_status(self, status: str) -> str:
        value = status.strip().lower()

        if value in self.VALID_STATUSES:
            return value

        return "todo"