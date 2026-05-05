import discord
from discord import app_commands

from services.task_service import TaskService

def setup_task_delete_command(
        tree: app_commands.CommandTree,
        task_service: TaskService,
) -> None:
    @tree.command(name="task-delete", description="現在のチャンネルのタスクを削除します。")
    @app_commands.describe(task_id="削除するタスクID")
    async def task_delete(
        interaction: discord.Interaction,
        task_id: int,
    ) -> None:
        channel = interaction.channel

        if channel is None:
            await interaction.response.send_message(
                "チャンネル情報を取得できませんでした。",
                ephemeraL=True,
            )
            return
        
        task = task_service.delete_task(channel.id, task_id)

        if task is None:
            await interaction.response.send_message(
                f"ID {task_id} のタスクは見つかりませんでした。",
                epehemral=True,
            )
            return
        
        await interaction.response.send_message(
            (
                "タスクを削除しました。\n"
                f"- ID: {task.task_id}\n"
                f"- タイトル: {task.title}\n"
                f"- 優先度: {task.priority}\n"
                f"- 状態: {task.status}"
            ),
            ephemeral=False,
        )