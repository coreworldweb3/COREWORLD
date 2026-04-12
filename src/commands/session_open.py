import discord
from discord import app_commands

from services.session_service import SessionService

def setup_session_open_command(tree: app_commands.CommandTree, session_service: SessionService) -> None:
    @tree.command(name="session-open", description="現在のチャンネルを開始します。")
    async def session_open(interaction: discord.Interaction) -> None:
        channel = interaction.channel

        if channel is None:
            await interaction.response.send_message(
                "チャンネル情報を取得できませんでした。",
                ephemeral=True,
            )
            return
        session = session_service.open_session(
            channel_id=channel.id,
            owner_id=interaction.user.id,
        )

        await interaction.response.send_message(
        (
            "セッションを開始しました。\n"
            f"- チャンネルID: {session.channel_id}\n"
            f"- 利用者ID: {session.owner_id}\n"
            f"- 状態: {session.status}\n"
            f"- 開始日時: {session.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        ),
        ephemeral=False,
        )