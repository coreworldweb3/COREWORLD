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
        description="自分の依頼を受付番号から確認します。",
    )
    @app_commands.describe(
        request_id="確認したい依頼の受付番号",
    )
    async def request_status(
        interaction: discord.Interaction,
        request_id: int,
    ) -> None:

        if request_id <= 0:
            await interaction.response.send_message(
                "受付番号には1以上の整数を指定してください。",
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
                "該当する依頼が見つからないか、閲覧権限がありません。",
                ephemeral=True,
            )
            return

        content = str(record["request_text"])
        if len(content) > 1200:
            content = content[:1200] + "...(以下省略)"

        content = discord.utils.escape_markdown(content)

        await interaction.response.send_message(
            (
                "**【依頼状況】**\n"
                f"受付番号： '{record['request_id']}'\n"
                f"状態： '{record['status']}'\n"
                f"受付日時 (UTC) ： {record['created_at']}\n\n"
                f"**依頼内容**\n{content}"
            ),
            ephemeral=True,
            allowed_mentions=discord.AllowedMentions.none(),
        )