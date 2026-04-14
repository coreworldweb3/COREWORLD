import os

import discord
from discord import app_commands
from dotenv import load_dotenv

from commands.session_open import setup_session_open_command
from services.session_service import SessionService


load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_GUILD_ID = os.getenv("DISCORD_GUILD_ID")

if not DISCORD_BOT_TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN が .env に設定されていません。")

if not DISCORD_GUILD_ID:
    raise ValueError("DISCORD_GUILD_ID が .env に設定されていません。")


intents = discord.Intents.default()


class CoreWorldBot(discord.Client):
    def __init__(self) -> None:
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.session_service = SessionService()

    async def setup_hook(self) -> None:
        setup_session_open_command(self.tree, self.session_service)

        guild = discord.Object(id=int(DISCORD_GUILD_ID))

        self.tree.copy_global_to(guild=guild)
        synced = await self.tree.sync(guild=guild)

        print(f"同期したコマンド数: {len(synced)}")

    async def on_ready(self) -> None:
        print(f"ログイン成功: {self.user}")


bot = CoreWorldBot()
bot.run(DISCORD_BOT_TOKEN)