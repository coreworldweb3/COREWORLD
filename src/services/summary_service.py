import os
from typing import Iterable

import discord
from openai import OpenAI


class SummaryService:
    """メッセージ一覧から簡易一覧またはOpenAI要約を作るサービス。"""

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-5.5")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def build_recent_summary(
        self,
        messages: Iterable[discord.Message],
        limit: int = 20,
    ) -> str:
        items = list(messages)

        if not items:
            return "対象メッセージが見つかりませんでした。"

        items.sort(key=lambda message: message.created_at)
        items = items[-limit:]

        formatted_messages = self._format_messages(items)

        if self.client is None:
            return self._build_fallback_summary(items)

        try:
            response = self.client.responses.create(
                model=self.model,
                input=[
                    {
                        "role": "system",
                        "content": (
                            "あなたはDiscord業務ハブBotの要約補助です。"
                            "与えられた会話ログを日本語で簡潔に整理してください。"
                            "出力形式は以下に厳密に従ってください。\n\n"
                            "【要点】\n"
                            "- 箇条書きで3〜5件\n\n"
                            "【タスク候補】\n"
                            "- 箇条書きで列挙。なければ『なし』\n\n"
                            "【決定事項候補】\n"
                            "- 箇条書きで列挙。なければ『なし』\n\n"
                            "【重要リンク候補】\n"
                            "- URL があれば列挙。なければ『なし』"
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"以下はDiscordチャンネルの直近{len(items)}件のメッセージです。\n\n"
                            f"{formatted_messages}"
                        ),
                    },
                ],
            )

            summary_text = getattr(response, "output_text", None)

            if summary_text and summary_text.strip():
                return summary_text.strip()

            return "OpenAIから要約結果を取得できませんでした。"

        except Exception as error:
            return (
                "OpenAI要約中にエラーが発生したため、簡易一覧を表示します。\n\n"
                f"エラー: {error}\n\n"
                f"{self._build_fallback_summary(items)}"
            )

    def _format_messages(self, messages: list[discord.Message]) -> str:
        lines: list[str] = []

        for message in messages:
            author_name = message.author.display_name
            created_at = message.created_at.strftime("%Y-%m-%d %H:%M:%S")

            content = message.content.strip()
            if not content:
                if message.attachments:
                    content = f"[添付ファイル {len(message.attachments)}件]"
                else:
                    content = "[本文なし]"

            if len(content) > 500:
                content = content[:500] + "..."

            lines.append(f"[{created_at}] {author_name}: {content}")

        return "\n".join(lines)

    def _build_fallback_summary(self, messages: list[discord.Message]) -> str:
        lines: list[str] = []
        lines.append("【直近メッセージの簡易まとめ】")
        lines.append(f"件数: {len(messages)}")
        lines.append("")

        for message in messages:
            author_name = message.author.display_name
            created_at = message.created_at.strftime("%Y-%m-%d %H:%M:%S")

            content = message.content.strip()
            if not content:
                if message.attachments:
                    content = f"[添付ファイル {len(message.attachments)}件]"
                else:
                    content = "[本文なし]"

            if len(content) > 120:
                content = content[:120] + "..."

            lines.append(f"- {created_at} | {author_name}")
            lines.append(f"  {content}")

        return "\n".join(lines)