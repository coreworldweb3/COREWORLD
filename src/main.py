import os

import discord
from discord import app_commands
from dotenv import load_dotenv

from commands.session_open import setup_session_open_command
from services.session_service import SessionService

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

if not DISCORD_BOT_TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN が .envに設定されていません。")

intents = discord.Intents.default()

class CoreWorldBot(discord.Client):
    def __init__(self) -> None:
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.session_service = SessionService()

    async def setup_hook(self) -> None:
        setup_session_open_command(self.tree, self.session_service)

    async def on_ready(self) -> None:
        print(f"ログイン成功: {self.user}")

    
bot = CoreWorldBot()
bot.run(DISCORD_BOT_TOKEN)