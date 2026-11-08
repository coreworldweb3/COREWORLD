from dataclasses import dataclass

@dataclass(frozen=True)
class Classification:
    category: str
    target_service: str | None
    reason: str
    requires_approval: bool = False


class RequestClassifier:
    SERVICE_KEYWORDS = {
        "google_calendar": ("googleカレンダー", "カレンダー", "calendar"),
        "gmail": ("gmail", "メール", "email"),
        "google_docs": ("googleドキュメント", "ドキュメント", "google docs"),
        "google_sheets": ("googleスプレッドシート", "スプレッドシート", "sheets"),
        "google_drive": ("googleドライブ", "google drive"),
    }

    MANUAL_KEYWORDS = (
        "荷物を発送",
        "荷物を郵送",
        "電話をかけ",
        "現地で対応",
        "買ってきて",
    )

    APPROVAL_KEYWORDS = (
        "送信",
        "削除",
        "共有",
        "公開",
        "権限変更",
        "予定を変更",
    )

    def classify(self, request_text: str) -> Classification:
        text = request_text.strip().casefold()

        if not text:
            return Classification(
                "needs_clarification", None, "依頼内容が空です。",
            )

        if any(word in text for word in self.MANUAL_KEYWORDS):
            return Classification(
                "manual_required", None, "人間による作業が必要な依頼です。",
            )

        matched = [
            service
            for service, keywords in self.SERVICE_KEYWORDS.items()
            if any(word in text for word in keywords)
        ]

        if len(matched) > 1:
            return Classification(
                "needs_clarification",
                None,
                "複数サービスを使う依頼です。個別の確認が必要です。",
            )

        if not matched:
            return Classification(
                "needs_clarification",
                None,
                "対象サービスを特定できませんでした。",
            )

        approval = any(
            word in text for word in self.APPROVAL_KEYWORDS
        )

        return Classification(
            category="google_candidate",
            target_service=matched[0],
            reason="Googleサービスによる処理の候補です。必要な入力情報と権限の確認が必要です。",
            requires_approval=approval,
        )