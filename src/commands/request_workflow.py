import logging
from typing import Literal

import discord

from discord import app_commands

from services.request_workflow_service import RequestWorkflowService

logger = logging.getLogger(__name__)

def setup_request_workflow_commands(
    tree: app_commands.CommandTree,
    workflow: RequestWorkflowService,
) -> None:

    @tree.command(
        name="request-approval-request",
        description="分類済み依頼の承認を申請します。",
    )
    @app_commands.describe(
        request_id="承認を申請する受付番号",
    )
    async def request_approval_request(
        interaction: discord.Interaction,
        request_id: int,
    ) -> None:

        if request_id <= 0:
            await interaction.response.send_message(
                "受付番号は1以上を指定してください。",
                ephemeral=True,
            )
            return

        try:
            success = workflow.request_approval(
                request_id=request_id,
                requester_id=interaction.user.id,
            )
        except Exception:
            logger.exception("承認申請に失敗しました")
            await interaction.response.send_message(
                "承認申請中にエラーが初声ーしました。",
                ephemeral=True,
            )
            return

        if not success:
            await interaction.response.send_message(
                "申請できませんでした。依頼者本人の"
                "Google連携候補・classfifed状態のみ対象です。",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            (
                "** 【承認申請を受け付けました】**\n"
                f"受付番号： `{request_id}`\n"
                "状態: `needs_approval`\n"
                "承認担当者による確認待ちです。\n"
                "※外部サービスはまだ実行しません。"
            ),
            ephemeral=True,
        )

    @tree.command(
        name="request-review",
        description="承認担当者が依頼を確認・承認・却下します。",
    )
    @app_commands.describe(
        request_id="対象の受付番号",
        action="view:確認 / approve:承認 / reject:却下",
        reason="却下理由、または承認時の補足",
    )
    async def request_review(
        interaction: discord.Interaction,
        request_id: int,
        action: Literal["view", "approve", "reject"] = "view",
        reason: str = "",
    ) -> None:

        print("[DEBUG] 実行者ID:", interaction.user.id)
        print("[DEBUG] 承認担当者ID:", workflow.approver_ids)

        if not workflow.is_approver(interaction.user.id):
            await interaction.response.send_message(
                "このコマンドを使用する権限がありません。",
                ephemeral=True,
            )
            return

        if request_id <= 0:
            await interaction.response.send_message(
                "受付番号は1以上を指定してください。",
                ephemeral=True,
            )
            return

        try:
            if action != "view":
                changed = workflow.decide(
                    request_id=request_id,
                    approver_id=interaction.user.id,
                    decision=action,
                    reason=reason,
                )

                if not changed:
                    await interaction.response.send_message(
                        "状態変更できませんでした。"
                        "承認待ちの依頼か確認してください。",
                        ephemeral=True,
                    )
                    return

            record = workflow.get_for_review(
                request_id=request_id,
                approver_id=interaction.user.id,
            ) 

        except ValueError as exc:
            await interaction.response.send_message(
                str(exc),
                ephemeral=True,
            )
            return
        except Exception:
            logger.exception("依頼レビューに失敗しました")
            await interaction.response.send_message(
                "依頼レビュー中にエラーが発生しました。",
                ephemeral=True,
            )
            return

        if record is None:
            await interaction.response.send_message(
                "依頼が見つかりません。",
                ephemeral=True,
            )
            return

        content = discord.utils.escape_markdown(
            str(record["request_text"])[:750]
        )

        reason_text = discord.utils.escape_markdown(
            str(record["classification_reason"] or "")[:300]
        )

        await interaction.response.send_message(
            (
                "** 【依頼レビュー】 **\n"
                f"受付番号: `{record['request_id']}`\n"
                f"状態: `{record['status']}`\n"
                f"対象サービス: `{record['target_service'] or '未特定'}`\n"
                f"分類理由: {reason_text}\n\n"
                f"**依頼内容**\n{content}\n\n"
                "※承認済みでもGoogleサービスは実行されません。"
            ),
            ephemeral=True,
            allowed_mentions=discord.AllowedMentions.none(),
        )