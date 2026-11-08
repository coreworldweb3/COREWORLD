import sys
import unittest
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] /"src")
)

from services.request_classifier import RequestClassifier

class testRequestclassifier(unittest.TestCase):

    def setUp(self):
        self.classifier = RequestClassifier()

    def test_calendar(self):
        result = self.classifier.classify(
        "Googleカレンダーに予定を登録して"
        )
        self.assertEqual(result.category, "google_candidate")
        self.assertEqual(result.target_service, "google_calendar")

    def test_gmail_send_requires_approval(self):
        result = self.classifier.classify(
            "Gmailでメールを送信して"
        )
        self.assertTrue(result.requires_approval)

    def test_manual_request(self):
        result = self.classifier.classify(
            "荷物を郵送してください"
        )
        self.assertEqual(result.category, "manual_required")

    def test_unknown_request(self):
        result = self.classifier.classify(
            "資料を作って"
        )
        self.assertEqual(result.category, "needs_clarification")

    def test_multiple_services(self):
        result = self.classifier.classify(
            "Gmailの内容をGoogleドライブに保存して"
        )
        self.assertEqual(result.category, "needs_clarification")

if __name__ == "__main__":
    unittest.main()