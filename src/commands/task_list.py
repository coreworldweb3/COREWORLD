import discord
from discord import app_commands

from services.task_service import TaskService

def setup_task_list_command(
        tree: app_commands.CommandTree,
        task_service: TaskService,
) -> None:
    @tree.command(name="task-list", description="現在のチャンネルのタスク一覧を表示します。")
    async def task_list(interaction: discord.Interaction) -> None:
        channel = interaction.channel

        if channel is None:
            await interaction.response.send_message(
                "チャンネル情報を取得できませんでした。",
                ephemeral=True,
            )
            return
        
        tasks = task_service.list_tasks(channel.id)

        if not tasks:
            await interaction.response.send_message(
                "このチャンネルにはまだタスクがありません。",
                ephemeral=False,
            )
            return
        
        lines: list[str] = []
        lines.append("【タスク一覧】")
        lines.append(f"件数: {len(tasks)}")
        lines.append("")

        for task in tasks:
            assignee_text = task.assignee if task.assignee else "未設定"
            description_text = task.description if task.description else "なし"

            lines.append(
                f"- ID: {task.task_id} | {task.title} | "
                f"priority={task.priority} | status={task.status}"
            )
            lines.append(f" 担当者: {assignee_text}")
            lines.append(f" 説明: {description_text}")
            lines.append(
                f" 登録日時: {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
            )

        message = "\n".join(lines)

        if len(message) > 1900:
            message = message[:1900] + "\n... (省略)"

        await interaction.response.send_message(message, ephemeral=False)