
import logging

import discord
from discord import app_commands

from services.request_service import RequestService


logger = logging.getLogger(__name__)


def setup_request_status_command(
    tree: app_commands.CommandTree,
    request_service: RequestService,
) -> None:

    @tree.command(
        name="request-status",
        description="自分の依頼の状態と分類結果を確認します。",
    )
    @app_commands.describe(
        request_id="確認する受付番号",
    )
    async def request_status(
        interaction: discord.Interaction,
        request_id: int,
    ) -> None:

        if request_id <= 0:
            await interaction.response.send_message(
                "受付番号は1以上で指定してください。",
                ephemeral=True,
            )
            return

        try:
            record = request_service.get_request(
                request_id=request_id,
                requester_id=interaction.user.id,
            )

        except Exception:
            logger.exception("依頼状況の取得に失敗しました")
            await interaction.response.send_message(
                "依頼状況の取得に失敗しました。",
                ephemeral=True,
            )
            return

        if record is None:
            await interaction.response.send_message(
                "依頼が見つからないか、閲覧権限がありません。",
                ephemeral=True,
            )
            return

        content = str(record["request_text"])

        if len(content) > 1200:
            content = content[:1200] + "…"

        content = discord.utils.escape_markdown(content)

        lines = [
            "**【依頼状況】**",
            f"受付番号: `{record['request_id']}`",
            f"状態: `{record['status']}`",
            f"受付日時（UTC）: {record['created_at']}",
        ]

        if record["classification_category"]:
            category = record["classification_category"]
            service = record["target_service"] or "未特定"
            approval = record["approval_status"] or "undetermined"
            reason = discord.utils.escape_markdown(
                str(record["classification_reason"] or "")
            )

            lines.extend([
                "",
                "**分類情報**",
                f"分類: `{category}`",
                f"対象サービス: `{service}`",
                f"承認判定: `{approval}`",
                f"判定理由: {reason}",
                f"分類日時（UTC）: {record['classified_at']}",
            ])

        lines.extend([
            "",
            "**依頼内容**",
            content,
        ])

        await interaction.response.send_message(
            "\n".join(lines),
            ephemeral=True,
            allowed_mentions=discord.AllowedMentions.none(),
        )
