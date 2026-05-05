import discord
from discord import app_commands

from services.task_service import TaskService

def setup_task_done_command(
        tree: app_commands.CommandTree,
        task_service: TaskService,
) -> None:
    @tree.command(name="task-done", description="現在のチャンネルのタスクを完了にします。")
    @app_commands.describe(task_id="官僚にするタスクID")
    async def task_done(
        interaction: discord.Interaction,
        task_id: int,
    ) -> None:
        channel = interaction.channel

        if channel is None:
            await interaction.response.send_message(
                "チャンネル情報を取得できませんでした。",
                ephemeral=True,
            )
            return
        
        task = task_service.mark_done(channel.id, task_id)

        if task is None:
            await interaction.response.send_message(
                f"ID {task_id} のタスクは見つかりませんでした。",
                ephemeral=True,
            )
            return
        
        await interaction.response.send_message(
            (
                "タスクを完了にしました。\n"
                f"- ID: {task.task_id}\n"
                f"- タイトル: {task.title}\n"
                f"- 優先度: {task.priority}\n"
                f"- 状態: {task.status}"
            ),
            ephemeral=False,
        )