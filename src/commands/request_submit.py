import logging
import os

import discord
from discord import app_commands

from services.request_service import RequestService

logger = logging.getLogger(__name__)

def setup_request_submit_command(
        tree: app_commands.CommandTree,
        request_service: RequestService,
) -> None:

    @tree.command(
        name="request-submit",
        description="新しい依頼を受け付けて保存します。",
    )
    @app_commands.describe(
        text="依頼したい内容",
    )
    async def request_submit(
        interaction: discord.Interaction,
        text:str,
    ) -> None:

        allowed_channel = os.getenv(
            "REQUEST_INTAKE_CHANNEL_ID",""
        ).strip()

        if allowed_channel and str(interaction.channel_id) != allowed_channel:
            await interaction.response.send_message(
                "このチャンネルでは依頼を受け付けていません。",
                ephemeral=True,
            )
            return

        if interaction.channel_id is None:
            await interaction.response.send_message(
                "チャンネル情報を取得できませんでした。",
                ephemeral=True,
            )
            return
        
        try:
            request_id = request_service.create_request(
                requester_id=interaction.user.id,
                source_channel_id=interaction.channel_id,
                source_guild_id=interaction.guild_id,
                request_text=text,
            )

        except Exception:
            logger.exception("依頼の保存に失敗しました")

            await interaction.response.send_message(
                "依頼の保存に失敗しました。管理者に確認してください。",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            (
                "依頼を受け付けました。\n"
                f"受付番号： '{request_id}'\n"
                "状態： 'received' (受付済み) \n\n"
                "※現投稿では依頼の保存のみ行います。"
                "Googleサービスへの実行はまだ行いません。"
            ),
            ephemeral=True,
        )