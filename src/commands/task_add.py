import discord
from discord import app_commands

from services.task_service import TaskService
def setup_task_add_command(
        tree: app_commands.CommandTree,
        task_service: TaskService,
) -> None:
    @tree.command(name="task-add", description="現在のチャンネルにタスクを追加します。")
    @app_commands.describe(
        title="タスク名",
        description="タスクの詳細説明（任意）",
        assignee="担当者名（任意）",
        priority="優先度 low / middle /high（任意）",
    )
    async def task_add(
        interaction: discord.Interaction,
        title: str,
        description: str = "",
        assignee: str = "",
        priority: str = "middle",
    ) -> None:
        channel = interaction.channel

        if channel is None:
            await interaction.response.send_message(
                "チャンネル情報を取得できませんでした。",
                ephemeral=True,
            )
            return
        
        task = task_service.add_task(
            channel_id=channel.id,
            created_by=interaction.user.id,
            title=title,
            description=description,
            assignee=assignee if assignee else None,
            priority=priority,
        )

        assignee_text = task.assignee if task.assignee else "未設定"
        description_text = task.description if task.description else "なし"

        await interaction.response.send_message(
            (
                "タスクを追加しました。\n"
                f"- ID: {task.task_id}\n"
                f"- タイトル:{task.title}\n"
                f"- 説明: {description_text}\n"
                f"- 担当者: {assignee_text}\n"
                f"- 優先度: {task.priority}\n"
                f"- 状態: {task.status}\n"
                f"- 登録日時: {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
            ),
            ephemeral=False,
        )