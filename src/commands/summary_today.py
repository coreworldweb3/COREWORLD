import discord
from discord import app_commands

from services.summary_service import SummaryService


def setup_summary_today_command(
    tree: app_commands.CommandTree,
    summary_service: SummaryService,
) -> None:
    @tree.command(name="summary-today", description="現在のチャンネルの直近メッセージを要約します。")
    async def summary_today(interaction: discord.Interaction) -> None:
        channel = interaction.channel

        if channel is None:
            await interaction.response.send_message(
                "チャンネル情報を取得できませんでした。",
                ephemeral=True,
            )
            return

        if not isinstance(channel, (discord.TextChannel, discord.Thread)):
            await interaction.response.send_message(
                "このコマンドはテキストチャンネルまたはスレッドでのみ使えます。",
                ephemeral=True,
            )
            return

        await interaction.response.defer(thinking=True)

        try:
            messages = [
                message
                async for message in channel.history(limit=20)
                if not message.author.bot
            ]
        except discord.Forbidden:
            await interaction.followup.send(
                "メッセージ履歴を読む権限がありません。",
                ephemeral=True,
            )
            return

        summary_text = summary_service.build_recent_summary(messages)

        if len(summary_text) > 1900:
            summary_text = summary_text[:1900] + "\n...（省略）"

        await interaction.followup.send(summary_text, ephemeral=False)