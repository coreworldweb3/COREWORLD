import discord
from discord import app_commands

from services.task_service import TaskService

def setup_task_move_command(
        tree: app_commands.CommandTree,
        task_service: TaskService,
) -> None:
    @tree.command(name="task-move", description="現在のチャンネルのタスク状態を変更します。")
    @app_commands.describe(
        task_id="状態を変更するタスクID",
        status="変更後の状態 todo / doing / waiting / done / archived",
    )
    async def task_move(
        interaction: discord.Interaction,
        task_id: int,
        status: str,
    ) -> None:
        channel = interaction.channel

        if channel is None:
            await interaction.response.send_message(
                "チャンネル情報を取得できませんでした。",
                ephemeral=True,
            )
            return
        
        normalized_status = status.strip().lower()
        valid_statuses = {"todo", "doing", "waiting", "done", "archived"}

        if normalized_status not in valid_statuses:
            await interaction.response.send_message(
                "状態は todo / doing / waiting / done / archivedのいずれかを指定してください。",
                ephemeral = True,
            )
            return
        
        task = task_service.move_task(channel.id, task_id, normalized_status)

        if task is None:
            await interaction.response.send_message(
                f"ID {task_id} のタスクは見つかりませんでした。",
                ephemral = True,
            )
            return
        
        await interaction.response.send_message(
            (
                "タスク状態を変更しました。\n"
                f"- ID: {task.task_id}\n"
                f"- タイトル: {task.title}\n"
                f"- 優先度: {task.priority}\n"
                f"- 新しい状態: {task.status}"
            ),
            ephemeral=False,
        )