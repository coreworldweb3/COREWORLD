import discord
from discord import app_commands

from connectors.trello_connector import TrelloConnector

def setup_trello_comment_command(
        tree: app_commands.CommandTree,
        trello_connector: TrelloConnector,
) -> None:
    @tree.command(name="trello-comment", description="Trelloカードにコメントを追加します。")
    @app_commands.describe(
        card_id="コメントを追加するTrelloカードID",
        comment="追加するコメント本文",
    )
    async def trello_comment(
        interaction: discord.Interaction,
        card_id: str,
        comment: str,
    ) -> None:
        await interaction.response.defer(thinking=True)

        try:
            action = trello_connector.add_comment(
                card_id=card_id,
                comment=comment,
            )
        except Exception as exc:
            print(f"[TRELLO COMMENT ERROR] {exc!r}")
            await interaction.followup.send(
                f"Trello カードへのコメント追加に失敗しました。\n{exc}",
                ephemeral=True,
            )
            return
        
        action_id = action.get("id", "(ID不明)")
        data = action.get("data", {})
        card = data.get("card", {})
        card_name = card.get("name","(カード名不明)")

        await interaction.followup.send(
            (
                "Trelloカードにコメントを追加しました。\n"
                f"- カード: {card_name}\n"
                f"- アクションID: {action_id}"
            ),
            ephemeral=False,
        )