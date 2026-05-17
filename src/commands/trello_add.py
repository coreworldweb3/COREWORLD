import discord
from discord import app_commands

from connectors.trello_connector import TrelloConnector


def setup_trello_add_command(
    tree: app_commands.CommandTree,
    trello_connector: TrelloConnector,
) -> None:
    @tree.command(name="trello-add", description="現在の内容をTrelloカードとして追加します。")
    @app_commands.describe(
        title="カードタイトル",
        description="カード詳細説明（任意）",
    )
    async def trello_add(
        interaction: discord.Interaction,
        title: str,
        description: str = "",
    ) -> None:
        await interaction.response.defer(thinking=True)

        try:
            card = trello_connector.create_card(
                title=title,
                description=description,
            )
        except Exception as exc:
            print(f"[TRELLO ERROR] {exc!r}")
            await interaction.followup.send(
                f"Trelloへのカード追加に失敗しました。\n(exc)",
                ephemeral=True,
            )
            return
        
        card_name = card.get("name", "(名称不明)")
        card_id = card.get("id", "(ID不明)")
        short_url = card.get("shortUrl", "(URLなし)")

        await interaction.followup.send(
            (
                "Trelloカードを作成しました。\n"
                f"- 名前: {card_name}\n"
                f"- ID: {card_id}\n"
                f"- URL: {short_url}"
            ),
            ephemeral=False,
        )