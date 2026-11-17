import os

import discord
from discord import app_commands
from dotenv import load_dotenv
from pathlib import Path

from commands.session_open import setup_session_open_command
from commands.summary_today import setup_summary_today_command
from commands.task_add import setup_task_add_command
from commands.task_delete import setup_task_delete_command
from commands.task_done import setup_task_done_command
from commands.task_list import setup_task_list_command
from commands.task_move import setup_task_move_command
from commands.trello_add import setup_trello_add_command
from commands.trello_move import setup_trello_move_command
from commands.trello_comment import setup_trello_comment_command
from commands.notion_course import CourseStartView, setup_notion_course_command
from connectors.trello_connector import TrelloConnector
from services.session_service import SessionService
from services.summary_service import SummaryService
from services.task_service import TaskService
from commands.request_submit import setup_request_submit_command
from commands.request_status import setup_request_status_command
from commands.request_list import setup_request_list_command
from commands.request_classify import setup_request_classify_command
from commands.request_workflow import setup_request_workflow_commands
from services.request_workflow_service import RequestWorkflowService
from services.request_service import RequestService

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"

load_dotenv(
    dotenv_path=ENV_PATH,
    override=True,
)

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_GUILD_ID = os.getenv("DISCORD_GUILD_ID")

if not DISCORD_BOT_TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN が .env に設定されていません。")

if not DISCORD_GUILD_ID:
    raise ValueError("DISCORD_GUILD_ID が .env に設定されていません。")


intents = discord.Intents.default()
intents.message_content = True


class CoreWorldBot(discord.Client):
    def __init__(self) -> None:
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.session_service = SessionService()
        self.summary_service = SummaryService()
        self.task_service = TaskService()
        self.trello_connector = TrelloConnector()
        self.request_service = RequestService()

        approver_ids = {
            int(value.strip())
            for value in os.getenv("REQUEST_APPROVER_IDS", "").split(",")
            if value.strip().isdigit()
        }

        self.workflow_service = RequestWorkflowService(
            db_path=self.request_service.db_path,
            approver_ids=approver_ids,
        )

        print(
            "[DEBUG] 承認担当者登録数:",
            len(self.workflow_service.approver_ids),
        )

    async def setup_hook(self) -> None:
        setup_session_open_command(self.tree, self.session_service)
        setup_summary_today_command(self.tree, self.summary_service)
        setup_task_add_command(self.tree, self.task_service)
        setup_task_list_command(self.tree, self.task_service)
        setup_task_done_command(self.tree, self.task_service)
        setup_task_move_command(self.tree, self.task_service)
        setup_task_delete_command(self.tree, self.task_service)
        setup_trello_add_command(self.tree, self.trello_connector)
        setup_trello_move_command(self.tree, self.trello_connector)
        setup_trello_comment_command(self.tree, self.trello_connector)
        setup_notion_course_command(self.tree)
        setup_request_submit_command(self.tree, self.request_service)
        setup_request_status_command(self.tree, self.request_service)
        setup_request_list_command(self.tree, self.request_service)
        setup_request_classify_command(self.tree, self.request_service)
        setup_request_workflow_commands(self.tree, self.workflow_service)
        self.add_view(CourseStartView())

        guild = discord.Object(id=int(DISCORD_GUILD_ID))
        self.tree.copy_global_to(guild=guild)
        synced = await self.tree.sync(guild=guild)

        print(f"同期したコマンド数: {len(synced)}")

    async def on_ready(self) -> None:
        print(f"ログイン成功: {self.user}")


if __name__ == "__main__":
    bot = CoreWorldBot()
    bot.run(DISCORD_BOT_TOKEN)
