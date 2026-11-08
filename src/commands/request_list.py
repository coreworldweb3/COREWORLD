import logging
import discord
from discord import app_commands

from services.request_service import RequestService

logger = logging.getLogger(__name__)

def setup_request_list_command(
        tree: app_commands.CommandTree,
        request_service: RequestService,
) -> None:

    @tree.command(
        name="request-list",
        description="自分が登録した依頼の一覧を表示します。",
    )
    @app_commands.describe(
        limit="表示件数 (1～20, 省略時10件)",
    )
    async def request_list(
        interaction: discord.Interaction,
        limit: int = 10,
    ) -> None:

        if not 1 < limit <= 20:
            await interaction.response.send_message(
                "表示件数は1～20の範囲で指定してください。",
                ephemeral=True,
            )
            return

        try:
            records = request_service.list_requests(
                requester_id=interaction.user.id,
                limit=limit,
            )

        except Exception:
            logger.exception("依頼一覧の取得に失敗しました")
            await interaction.response.send_message(
                "依頼一覧の取得に失敗しました。",
                ephemeral=True,
            )
            return

        if not records:
            await interaction.response.send_message(
                "登録済みの依頼はありません。",
                ephemeral=True,
            )
            return

        lines = ["** 【あなたの依頼一覧】**"]

        for record in records:
            content = str(record["request_text"])
            content = content.replace("\r", " ").replace("\n", " ")

            if len(content) > 65:
                content = content[:65] + "_"

            content = discord.utils.escape_markdown(content)

            lines.append(
                f"`#{record['request_id']}` "
                f"[{record['status']}] {content}"
            )

            lines.append(
                "\n詳細は '/request-status' で確認できます。"
            )

            await interaction.response.send_message(
                "\n".join(lines),
                ephemeral=True,
                allowed_mentions=discord.AllowedMentions.none(),
            )