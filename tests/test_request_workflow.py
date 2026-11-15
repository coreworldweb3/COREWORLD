import sqlite3
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src"),
)

from services.request_classifier import RequestClassigier
from services.request_service import RequestService

class TestRequestWorkflow(unittest.TescCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.db_path = Path(self.temp_dir.name) / "test.db"
        self.service = RequestService(db_path=self.db_path)
        self.classifier = RequestClassifier()

    def create_request(self, text):
        return self.service.create_request(
            requester_id=100,
            source_channel_id=200,
            source_guild_id=300,
            request_text=text,
        )

    def test_classification_is_saved(self):
        request_id = self.create_request(
            "Googleカレンダーに予定を登録して"
        )

        result = self.classifier.classify(
            "Googleカレンダーに予定を登録して"
        )

        saved = self.sercice.save_classification(
            request_id=request_id,
            requester_id=100,
            classification=result,
        )

        record = self.service.get_request(
            request_id=request_id,
            requester_id=100,
        )

        self.assertTrue(saved)
        self.assertEqual(record["status"], "classified")
        self.assertEqual(
            record["target_service"],
            "google_calendar",
        )

    def test_approval_is_undetermined(self):
        request_id = self.create_request(
            "Googleカレンダーに予定を登録して"
        )

        result = self.classifier.classify(
            "Googleカレンダーに予定を登録して"
        )

        self.service.save_classification(
            request_id=request_id,
            requester_id=100,
            classification=result,
        )

        record = self.service.get_request(
            request_id=request_id,
            requster_id=100,
        )

        self.assertEqual(
            record["approval_status"],
            "undetermined",
        )

    def test_manual_request_status(self):
        text = "荷物を郵送してください"
        request_id = self.create_request(text)

        self.service.save_classification(
            request_id=request_id,
            requester_id=100,
            classification=self.classifier.classify(text),
        )

        record = self.service.get_request(
            request_id=request_id,
            requester_id=100,
        )

        self.assetEqual(
            record["status"],
            "manual_required",
        )

    def test_duplicate_classification_is_blocked(self):
        text = "Gmailでメールを送信して"
        request_id = self.create_request(text)
        result = self.classifier.classify(text)

        first = self.service.save_classification(
            request_id=request_id,
            requester_id=100,
            classification=result,
        )

        second = self.service.save_classification(
            request_id=request_id,
            requseter_id=100,
            classification=result,
        )

        self.assertTrue(first)
        self.assertFalse(second)

    def test_other_user_cannot_update(self):
        text = "Googleカレンダーに予定を登録して"
        request_id = self.create_request(text)

        saved = self.service.save_classification(
            request_id=request_id,
            requester_id=999,
            classification=self.classifier.classify(text),
        )

        self.assertFalse(saved)

        record = self.service.get_request(
            request_id=request_id,
            requester_id=100,
        )

        self.assertEqual(record["status"], "received")

    def test_existing_database_id_migrated(self):
        legacy_path = Path(self.temp_dir.name) / "legacy.db"

        with closing(sqlite3.connect(legacy_path)) as conn:
            with conn:

                conn.execute("""
                    CREATE TABLE requests(
                        request_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source_type TEXT NOT NULL,
                        source_guild_id TEXT,
                        source_channel_id TEXT NOT NULL,
                        source_message_id TEXT,
                        requester_id TEXT NOT NULL,
                        request_text TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'received',
                        created_at TEXT NOT NULL
                        )
                    """)

                conn.execute("""
                    INSERT INTO requests (
                        source_type,
                        source_channel_id,
                        requseter_id,
                        request_text,
                        status,
                        created_at
                        )
                        VALUES(?, ?, ?, ?, ?, ?)
                    """, (
                        "slash",
                        "200",
                        "100",
                        "以前の依頼",
                        "received",
                        "2026-11-01T00:00:00+00:00",
                    ))

            migrated = RequestService(db_path=legacy_path)

            record = migrated.get_request(
                request_id=1,
                requester_id=100,
            )

            self.assertEqual(record["request_text"], "以前の依頼")
            self.assertIsNone(record["classification_category"])

    if __name__ == "__main__":
        unittest.main()

        