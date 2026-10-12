import importlib
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import discord
from discord import app_commands
from commands.notion_course import CourseStartView, LessonAnswerView, setup_notion_course_command
from services.notion_course_content import course_embed, lesson_embed, answer_embed, SAMPLE_CSV


def interaction_mock():
    interaction = MagicMock()
    interaction.response.send_message = AsyncMock()
    interaction.response.defer = AsyncMock()
    interaction.followup.send = AsyncMock()
    interaction.channel = MagicMock(spec=discord.TextChannel)
    interaction.channel.send = AsyncMock(return_value=MagicMock(jump_url="https://discord.com/channels/1/2/3"))
    interaction.permissions = discord.Permissions(manage_guild=True)
    return interaction


class ContentTests(unittest.TestCase):
    def test_discord_embed_limits(self):
        for embed in (course_embed(), lesson_embed(), answer_embed()):
            self.assertLessEqual(len(embed), 6000)
            self.assertLessEqual(len(embed.title or ""), 256)
            self.assertLessEqual(len(embed.description or ""), 4096)
            self.assertLessEqual(len(embed.fields), 25)
            for field in embed.fields:
                self.assertLessEqual(len(field.name), 256)
                self.assertLessEqual(len(field.value), 1024)

    def test_sample_csv_matches_user_data(self):
        import csv
        rows = list(csv.DictReader(SAMPLE_CSV.splitlines()))
        self.assertEqual([row["ID"] for row in rows], ["P001", "P002", "P003"])
        self.assertEqual([row["担当"] for row in rows], ["田中", "佐藤", "鈴木"])


class InteractionTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = discord.Client(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self.client)
        setup_notion_course_command(self.tree)
        self.command = self.tree.get_command("notion-course")

    async def asyncTearDown(self):
        await self.client.close()

    async def test_start_button_survives_restart(self):
        before, after = CourseStartView(), CourseStartView()
        self.assertTrue(after.is_persistent())
        self.assertEqual(before.children[0].custom_id, after.children[0].custom_id)
        interaction = interaction_mock()
        await after.children[0].callback(interaction)
        args = interaction.response.send_message.call_args.kwargs
        self.assertTrue(args["ephemeral"])
        self.assertIsInstance(args["view"], LessonAnswerView)
        self.assertTrue(args["file"].fp.read().startswith(b"\xef\xbb\xbf"))
        args["file"].close()

    async def test_multiple_learners_get_separate_materials(self):
        view = CourseStartView()
        first, second = interaction_mock(), interaction_mock()
        await view.children[0].callback(first)
        await view.children[0].callback(second)
        a = first.response.send_message.call_args.kwargs
        b = second.response.send_message.call_args.kwargs
        self.assertIsNot(a["view"], b["view"])
        self.assertTrue(a["ephemeral"] and b["ephemeral"])
        a["file"].close()
        b["file"].close()

    async def test_answer_is_private(self):
        interaction = interaction_mock()
        await LessonAnswerView().children[0].callback(interaction)
        self.assertTrue(interaction.response.send_message.call_args.kwargs["ephemeral"])

    async def test_publish_public_message_and_private_receipt(self):
        interaction = interaction_mock()
        await self.command.callback(interaction)
        interaction.channel.send.assert_awaited_once()
        self.assertTrue(interaction.followup.send.call_args.kwargs["ephemeral"])
        self.assertIsInstance(interaction.channel.send.call_args.kwargs["view"], CourseStartView)

    async def test_runtime_permission_check(self):
        interaction = interaction_mock()
        for check in self.command.checks:
            self.assertTrue(check(interaction))
        interaction.permissions = discord.Permissions.none()
        with self.assertRaises(app_commands.MissingPermissions):
            for check in self.command.checks:
                check(interaction)

    async def test_permission_error_message(self):
        interaction = interaction_mock()
        await self.command.on_error(interaction, app_commands.MissingPermissions(["manage_guild"]))
        self.assertIn("サーバー管理", interaction.response.send_message.call_args.args[0])

    async def test_dm_or_thread_is_rejected(self):
        interaction = interaction_mock()
        interaction.channel = MagicMock(spec=discord.DMChannel)
        await self.command.callback(interaction)
        self.assertIn("テキストチャンネル", interaction.response.send_message.call_args.args[0])

    async def test_bot_without_send_permission(self):
        interaction = interaction_mock()
        interaction.channel.send.side_effect = discord.Forbidden(MagicMock(status=403, reason="Forbidden"), "Forbidden")
        await self.command.callback(interaction)
        self.assertIn("権限", interaction.followup.send.call_args.args[0])

    async def test_discord_failure_has_private_feedback(self):
        interaction = interaction_mock()
        interaction.channel.send.side_effect = discord.HTTPException(MagicMock(status=500, reason="Server Error"), "Server Error")
        with self.assertLogs("commands.notion_course", level="ERROR"):
            await self.command.callback(interaction)
        self.assertTrue(interaction.followup.send.call_args.kwargs["ephemeral"])

    async def test_existing_commands_preserved_and_persistent_view_registered(self):
        # .env・DB・Trello・Discord通信を使わず本番のsetup_hookを検証する。
        with patch.dict(os.environ, {"DISCORD_BOT_TOKEN": "offline-test", "DISCORD_GUILD_ID": "1"}), patch("dotenv.load_dotenv"), patch.object(discord.Client, "run") as run:
            main = importlib.import_module("main")
            run.assert_not_called()
        with patch.object(main, "SessionService"), patch.object(main, "SummaryService"), patch.object(main, "TaskService"), patch.object(main, "TrelloConnector"):
            bot = main.CoreWorldBot()
        with patch.object(bot.tree, "sync", new=AsyncMock(return_value=[])), patch.object(bot, "add_view") as add_view:
            await bot.setup_hook()
        expected = {"session-open", "summary-today", "task-add", "task-list", "task-done", "task-move", "task-delete", "trello-add", "trello-move", "trello-comment", "notion-course"}
        self.assertEqual({command.name for command in bot.tree.get_commands()}, expected)
        self.assertEqual({command.name for command in bot.tree.get_commands(guild=discord.Object(id=1))}, expected)
        self.assertTrue(add_view.call_args.args[0].is_persistent())
        await bot.close()


if __name__ == "__main__":
    unittest.main()
