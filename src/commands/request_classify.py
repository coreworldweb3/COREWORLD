import logging

import discord
from discord import app_commands

from services.request_service import RequestService
from services.request_classifier import RequestClassifier

logger = logging.getLogger(__name__)

def setup_request_classify_command(
tree: app_commands.CommandTree,
request_service: RequestService,
) -> None:

    classifier = RequestClassifier()

    @tree.command(
        name="request_classify",
        description="受付済み依頼をルールベースで分類します。",
    )
    @app_commands.describe(
        request_id="分類する依頼の受付番号",
    )
    async def request_classify(
        interaction: discord.Interaction,
        request_id: int,
    ) -> None:

        if request_id <= 0:
            await interaction.response.send_message(
                "受付番号は1以上で指定してください。",
                ephemeral=True,
            )
            return

        try:
            record = request_service.get_request(
                request_id=request_id,
                requester_id=interaction.user.id,
            )

            if record is None:
                await interaction.response.send_message(
                    "依頼が見つからないか、閲覧権限がありません。",
                    ephemeral=True,
                )
                return

            result = classifier.classify(
                str(record["request_text"])
            )

        except Exception:
            logger.exception("依頼分類に失敗しました")
            await interaction.response.send_message(
                "依頼分類中にエラーが発生しました。",
                ephemeral=True,
            )
            return

        labels = {
            "google_candidate": "Google連携候補",
            "manual_required":"手動対応が必要",
            "needs_clarification": "要確認",
        }

        label = labels.get(result.category, result.category)
        service = result.target_service or "未特定"
        approval = "要承認候補" if result.requires_approval else "未判定"

        await interaction.response.send_message(
            (
                "** 【依頼分類結果】 **\n"
                f"受付番号： `{request_id}`\n"
                f"分類： **{label}**\n"
                f"対象サービス： `{service}`\n"
                f"追加承認： {approval}\n"
                f"理由： {result.reason}\n\n"
                "※試験版の分類結果です。"
                "外部サービスへの操作やDBへの分類結果保存は行いません。"
            ),
            ephemeral=True,
            allowed_mentions=discord.AllowedMentions.none(),
        )