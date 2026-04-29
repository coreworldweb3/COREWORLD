import os

import discord
from discord import app_commands
from dotenv import load_dotenv

from commands.session_open import setup_session_open_command
from commands.summary_today import setup_summary_today_command
from commands.task_add import setup_task_add_command
from services.session_service import SessionService
from services.summary_service import SummaryService
from services.task_service import TaskService


load_dotenv()

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

    async def setup_hook(self) -> None:
        setup_session_open_command(self.tree, self.session_service)
        setup_summary_today_command(self.tree, self.summary_service)
        setup_task_add_command(self.tree, self.task_service)

        guild = discord.Object(id=int(DISCORD_GUILD_ID))
        self.tree.copy_global_to(guild=guild)
        synced = await self.tree.sync(guild=guild)

        print(f"同期したコマンド数: {len(synced)}")

    async def on_ready(self) -> None:
        print(f"ログイン成功: {self.user}")


bot = CoreWorldBot()
bot.run(DISCORD_BOT_TOKEN)