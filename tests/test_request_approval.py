import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from contextlib import closing

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src"),
)

from services.request_classifier import RequestClassifier
from services.request_service import RequestService
from services.request_workflow_service import RequestWorkflowService

class TestRequestApproval(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.db_path = Path(self.temp_dir.name) / "test.db"

        self.service = RequestService(db_path=self.db_path)
        self.classifier = RequestClassifier()
        self.workflow = RequestWorkflowService(
            db_path=self.db_path,
            approver_ids={900},
        )

    def create_classified(self, text):
        request_id = self.service.create_request(
            requester_id=100,
            source_channel_id=200,
            source_guild_id=300,
            request_text=text,
        )

        result = self.classifier.classify(text)

        self.assertTrue(
            self.service.save_classification(
                request_id=request_id,
                requester_id=100,
                classification=result,
            )
        )

        return request_id

    def create_pending(self):
        request_id = self.create_classified(
            "Googleカレンダーに予定を登録してください"
        )

        self.assertTrue(
            self.workflow.request_approval(
                request_id=request_id,
                requester_id=100,
            )
        )

        return request_id

    def text_request_approval(self):
        request_id = self.create_pending()

        record = self.service.get_request(
            request_id=request_id,
            requester_id=100,
        )

        self.assertEqual(record["status"], "needs_approval")
        self.assertEqual(record["approval_status"], "pending")

    def test_unclassified_request_is_blocked(self):
        request_id = self.service.create_request(
            requester_id=100,
            source_channel_id=200,
            source_guild_id=300,
            request_text="まだ分類していない依頼",
        )

        self.assertFalse(
            self.workflow.request_approval(
                request_id=request_id,
                requester_id=100,
            )
        )

    def test_manual_request_id_blocked(self):
        request_id = self.create_classified(
            "荷物を郵送してください"
        )

        self.assertFalse(
            self.workflow.request_approval(
                request_id=request_id,
                requester_id=100,
            )
        )

    def test_pther_requester_id_blocked(self):
        request_id = self.create_classified(
            "Googleカレンダーに予定を登録して"
        )

        self.assertFalse(
            self.workflow.request_approval(
                request_id=request_id,
                requester_id=999,
            )
        )

    def test_unauthorized_review_is_blocked(self):
        request_id = self.create_pending()

        with self.assertRaises(PermissionError):
            self.workflow.get_for_review(
                request_id=request_id,
                approver_id=999,
            )

    def test_approval(self):
        request_id = self.create_pending()

        self.assertTrue(
            self.workflow.decide(
                request_id=request_id,
                approver_id=900,
                decision="approve",
            )
        )

        record = self.service.get_request(
            request_id=request_id,
            requester_id=100,
        )

        self.assertEqual(record["status"], "approved")
        self.assertEqual(record["approval_status"], "approved")

    def test_rejection_requires_reason(self):
        request_id = self.create_pending()

        with self.assertRaises(ValueError):
            self.workflow.decide(
                request_id=request_id,
                approver_id=900,
                decision="reject",
            )

    def test_rejection(self):
        request_id = self.create_pending()

        self.assertTrue(
            self.workflow.decide(
                request_id=request_id,
                approver_id=900,
                decision="reject",
                reason="実施日時が未確定です",
            )
        )

        record = self.service.get_request(
            request_id=request_id,
            requester_id=100,
        )

        self.assertEqual(record["status"], "rejected")

    def test_duplicate_approval_is_blocked(self):
        request_id = self.create_pending()

        self.assertTrue(
            self.workflow.decide(
                request_id=request_id,
                approver_id=900,
                decision="approve",
            )
        )

        self.assertFalse(
            self.workflow.decide(
                request_id=request_id,
                approver_id=900,
                decision="approve",
            )
        )

    def test_unauthorized_approval_is_blocked(self):
        request_id = self.create_pending()

        with self.assertRaises(PermissionError):
            self.workflow.decide(
                request_id=request_id,
                approver_id=999,
                decision="approve",
            )

    def test_history_is_saved(self):
        request_id = self.create_pending()

        self.workflow.decide(
            request_id=request_id,
            approver_id=900,
            decision="approve",
        )

        with closing(sqlite3.connect(self.db_path)) as conn:
            rows = conn.execute(
                """
                SELECT from_status, to_status, action
                FROM request_status_history
                WHERE request_id = ?
                ORDER BY history_id
                """,
                (request_id,),
            ).fetchall()

        self.assertEqual(
            rows,
            [
                (
                    "classified",
                    "needs_approval",
                    "approval_requested",
                ),
                (
                    "needs_approval",
                    "approved",
                    "approve",
                ),
            ],
        )

if __name__ == "__main__":
    unittest.main()
