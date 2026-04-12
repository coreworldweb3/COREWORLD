from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

@dataclass
class SessionInfo:
    channel_id: int
    owner_id: int
    status: str
    created_at: datetime

class SessionService:
    """セッション情報を簡易的に管理するサービス。"""

    def __init__(self) -> None:
        self._sessions: Dict[int, SessionInfo] = {}

    def open_session(self, channel_id: int, owner_id: int) -> SessionInfo:
        """指定チャンネルにセッションを作成または上書きする。"""
        session = SessionInfo(
            channel_id=channel_id,
            owner_id=owner_id,
            status="open",
            created_at=datetime.now(),
        )
        self._sessions[channel_id] = session
        return session
    
    def get_session(self, channel_id: int) -> Optional[sessionInfo]:
        """指定チャンネルのセッションを取得する。"""
        return self._sessions.get(channel_id)
    
    def clear_session(self, channel_id: int) -> bool:
        """指定チャンネルのセッションを削除する。"""
        if channel_id in self._sessions:
            del self._sessions[channel_id]
            return True
        return False