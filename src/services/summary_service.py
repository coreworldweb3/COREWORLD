from typing import Iterable

import discord

class SummaryService:
    """メッセージ一覧から簡易サマリー文字列を作るサービス。"""

    def build_recent_summary(
            self,
            messages: Iterable[discord.Message],
            limit: int = 20,
    ) -> str:
        items = list(messages)

        if not items:
            return "対象メッセージが見つかりませんでした。"
        
        #古い順に並べ替え
        items.sort(key=lambda message: message.created_at)

        #表示件数を制限
        items = items[-limit:]

        lines: list[str] = []
        lines.append("【直近メッセージの簡易まとめ】")
        lines.append(f"件数：{len(items)}")
        lines.append("")

        for message in items:
            author_name = message.author.display_name
            created_at = message.created_at.strftime("%Y-%m-%d %H:%M:%S")

            content = message.content.strip()
            if not content:
                if message.attachments:
                    content = f"[添付ファイル {len(message.attachments)}件]"
                else:
                    content = "[本文なし]"

            #長すぎる本文は切る
            if len(content) > 120:
                content = content[:120] + "..."

            lines.append(f"- {created_at} | {author_name}")
            lines.append(f"  {content}")
        return "\n".join(lines)