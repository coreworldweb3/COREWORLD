from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


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
    """タスク情報を簡易的に管理するサービス。"""

    def __init__(self) -> None:
        self._tasks_by_channel: Dict[int, List[TaskInfo]] = {}
        self._sequence: int = 1

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

        task = TaskInfo(
            task_id=self._sequence,
            channel_id=channel_id,
            created_by=created_by,
            title=title.strip(),
            description=description.strip(),
            assignee=assignee.strip() if assignee else None,
            priority=normalized_priority,
            status="todo",
            created_at=datetime.now(),
        )

        if channel_id not in self._tasks_by_channel:
            self._tasks_by_channel[channel_id] = []

        self._tasks_by_channel[channel_id].append(task)
        self._sequence += 1
        return task

    def list_tasks(self, channel_id: int) -> List[TaskInfo]:
        return list(self._tasks_by_channel.get(channel_id, []))

    def find_task(self, channel_id: int, task_id: int) -> Optional[TaskInfo]:
        tasks = self._tasks_by_channel.get(channel_id, [])
        for task in tasks:
            if task.task_id == task_id:
                return task
        return None

    def mark_done(self, channel_id: int, task_id: int) -> Optional[TaskInfo]:
        task = self.find_task(channel_id, task_id)
        if task is None:
            return None

        task.status = "done"
        return task

    def _normalize_priority(self, priority: str) -> str:
        value = priority.strip().lower()

        if value in {"low", "middle", "high"}:
            return value

        return "middle"