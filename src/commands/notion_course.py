"""Notion学習案内と第1回。業務データや外部サービスを更新しない。"""

import io
import logging

import discord
from discord import app_commands

from services.notion_course_content import course_embed, lesson_embed, answer_embed, SAMPLE_CSV

logger = logging.getLogger(__name__)


class CourseStartView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(
        label="第一回の学習を始める",
        style=discord.ButtonStyle.success,
        custom_id="coreworld:notion-course:v1:lesson-1",
    )
    async def start_lesson(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_message(
            embed=lesson_embed(),
            file=discord.File(io.BytesIO(SAMPLE_CSV.encode("utf-8-sig")), filename="notion_course_projects.csv"),
            view=LessonAnswerView(),
            ephemeral=True,
            allowed_mentions=discord.AllowedMentions.none(),
        )


class LessonAnswerView(discord.ui.View):
    def __init__(self) -> None:
        # 本人向けメッセージのボタンは15分有効。案内から何度でも再開できる。
        super().__init__(timeout=900)

    @discord.ui.button(label="模範解答・理解度チェック", style=discord.ButtonStyle.primary)
    async def show_answer(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_message(embed=answer_embed(), ephemeral=True)


def setup_notion_course_command(tree: app_commands.CommandTree) -> None:
    @tree.command(name="notion-course", description="Notion学習コースの案内と開始ボタンをこのチャンネルに投稿します。")
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.checks.has_permissions(manage_guild=True)
    async def notion_course(interaction: discord.Interaction) -> None:
        if not isinstance(interaction.channel, discord.TextChannel):
            await interaction.response.send_message("サーバーのテキストチャンネルで実行してください。", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            message = await interaction.channel.send(
                embed=course_embed(),
                view=CourseStartView(),
                allowed_mentions=discord.AllowedMentions.none(),
            )
        except discord.Forbidden:
            await interaction.followup.send(
                "投稿できません。Botの「チャンネルを見る」「メッセージを送信」「埋め込みリンク」権限を確認してください。",
                ephemeral=True,
            )
            return
        except discord.HTTPException:
            logger.exception("Notion学習案内の投稿に失敗")
            await interaction.followup.send("Discordへの投稿に失敗しました。チャンネルを確認してから再試行してください。", ephemeral=True)
            return
        await interaction.followup.send(f"学習案内を投稿しました。\n{message.jump_url}", ephemeral=True)

    @notion_course.error
    async def notion_course_error(interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("この投稿には「サーバー管理」権限が必要です。", ephemeral=True)
            return
        raise error
