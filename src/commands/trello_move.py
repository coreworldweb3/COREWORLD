import discord
from discord import app_commands

from connectors.trello_connector import TrelloConnector


def setup_trello_move_command(
    tree: app_commands.CommandTree,
    trello_connector: TrelloConnector,
) -> None:
    @tree.command(name="trello-move", description="Trelloカードを別の列へ移動します。")
    @app_commands.describe(
        card_id="移動するTrelloカードID",
        target_status="移動先 todo / doing / done",
    )
    async def trello_move(
        interaction: discord.Interaction,
        card_id: str,
        target_status: str,
    ) -> None:
        await interaction.response.defer(thinking=True)

        try:
            card = trello_connector.move_card(
                card_id=card_id,
                target_status=target_status,
            )
        except Exception as exc:
            print(f"[TRELLO MOVE ERROR] {exc!r}")
            await interaction.followup.send(
                f"Trello カードの移動に失敗しました。\n{exc}",
                ephemeral=True,
            )
            return

        card_name = card.get("name", "(名称不明)")
        card_id_result = card.get("id", "(ID不明)")
        short_url = card.get("shortUrl", "(URLなし)")
        list_id = card.get("idList", "(リスト不明)")

        await interaction.followup.send(
            (
                "Trelloカードを移動しました。\n"
                f"- 名前: {card_name}\n"
                f"- ID: {card_id_result}\n"
                f"- 移動先リストID: {list_id}\n"
                f"- URL: {short_url}"
            ),
            ephemeral=False,
        )