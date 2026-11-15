
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
        name="request-classify",
        description="受付済み依頼を分類して保存します。",
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

            if record["classification_category"] is None:
                result = classifier.classify(
                    str(record["request_text"])
                )

                saved = request_service.save_classification(
                    request_id=request_id,
                    requester_id=interaction.user.id,
                    classification=result,
                )

                if not saved:
                    logger.warning(
                        "依頼分類を保存できませんでした: %s",
                        request_id,
                    )

            record = request_service.get_request(
                request_id=request_id,
                requester_id=interaction.user.id,
            )

            if record is None or record["classification_category"] is None:
                await interaction.response.send_message(
                    "分類結果を保存できませんでした。"
                    "依頼の現在の状態を確認してください。",
                    ephemeral=True,
                )
                return

        except Exception:
            logger.exception("依頼分類・保存に失敗しました")
            await interaction.response.send_message(
                "依頼分類中にエラーが発生しました。",
                ephemeral=True,
            )
            return

        labels = {
            "google_candidate": "Google連携候補",
            "manual_required": "手動対応が必要",
            "needs_clarification": "要確認",
        }

        category = record["classification_category"]
        label = labels.get(category, category)
        service = record["target_service"] or "未特定"

        approval_labels = {
            "required": "要承認候補",
            "undetermined": "未判定",
            "not_required": "追加承認不要",
        }

        approval = approval_labels.get(
            record["approval_status"],
            "未判定",
        )

        reason = discord.utils.escape_markdown(
            str(record["classification_reason"] or "")
        )

        await interaction.response.send_message(
            (
                "**【依頼分類結果】**\n"
                f"受付番号: `{request_id}`\n"
                f"分類: **{label}**\n"
                f"対象サービス: `{service}`\n"
                f"状態: `{record['status']}`\n"
                f"追加承認: {approval}\n"
                f"理由: {reason}\n\n"
                "分類結果をSQLiteに保存しました。\n"
                "※Googleサービスへの操作はまだ行いません。"
            ),
            ephemeral=True,
            allowed_mentions=discord.AllowedMentions.none(),
        )
