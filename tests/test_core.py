import os
import shutil
import tempfile
import unittest
import datetime
from pathlib import Path

from core.scanner import scan_directory, format_folder_name, format_file_size
from core.organizer import OrganizerEngine
from core.transaction import TransactionManager


class TestFileOrganizerCore(unittest.TestCase):
    def setUp(self):
        # Create isolated temporary directory
        self.test_dir = tempfile.mkdtemp(prefix="test_file_org_")
        
        # Create test files with distinct names
        self.file1 = os.path.join(self.test_dir, "document_a.txt")
        self.file2 = os.path.join(self.test_dir, "photo_b.jpg")
        self.file3 = os.path.join(self.test_dir, "report_c.pdf")

        for fpath, content in [(self.file1, "Content A"), (self.file2, "Content B"), (self.file3, "Content C")]:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_scanner_detects_files(self):
        items = scan_directory(self.test_dir, date_source="Date Modified", folder_pattern="YYYY-MM-DD")
        self.assertEqual(len(items), 3)
        names = [item["name"] for item in items]
        self.assertIn("document_a.txt", names)
        self.assertIn("photo_b.jpg", names)
        self.assertIn("report_c.pdf", names)

    def test_folder_formatting(self):
        dt = datetime.datetime(2026, 10, 17, 14, 30)
        self.assertEqual(format_folder_name(dt, "YYYY-MM-DD"), "2026-10-17")
        self.assertEqual(format_folder_name(dt, "DD-MM-YYYY"), "17-10-2026")
        self.assertEqual(format_folder_name(dt, "YYYY_MM_DD"), "2026_10_17")
        self.assertEqual(format_folder_name(dt, "YYYY.MM.DD"), "2026.10.17")

    def test_file_size_formatting(self):
        self.assertEqual(format_file_size(500), "500 B")
        self.assertEqual(format_file_size(2048), "2.0 KB")
        self.assertEqual(format_file_size(5 * 1024 * 1024), "5.0 MB")

    def test_execute_batch_and_undo_rollback(self):
        organizer = OrganizerEngine(self.test_dir)
        items = scan_directory(self.test_dir, date_source="Date Modified", folder_pattern="YYYY-MM-DD")
        self.assertEqual(len(items), 3)

        # Execute organize
        report = organizer.execute_batch(items, collision_policy="auto_rename")
        self.assertEqual(report["moved"], 3)
        self.assertEqual(report["errors_count"], 0)

        # Original files should not exist in root
        self.assertFalse(os.path.exists(self.file1))
        self.assertFalse(os.path.exists(self.file2))
        self.assertFalse(os.path.exists(self.file3))

        # Files should exist in destination
        today_folder = datetime.datetime.now().strftime("%Y-%m-%d")
        dest_dir = os.path.join(self.test_dir, today_folder)
        self.assertTrue(os.path.exists(dest_dir))
        self.assertTrue(os.path.exists(os.path.join(dest_dir, "document_a.txt")))

        # Test Undo Rollback
        tx_manager = TransactionManager(self.test_dir)
        self.assertTrue(tx_manager.can_undo())
        undo_res = tx_manager.rollback_last_batch()
        self.assertEqual(undo_res["reverted"], 3)
        self.assertEqual(undo_res["failed"], 0)

        # Original files must be restored!
        self.assertTrue(os.path.exists(self.file1))
        self.assertTrue(os.path.exists(self.file2))
        self.assertTrue(os.path.exists(self.file3))

        # The empty destination folder should have been cleaned up
        self.assertFalse(os.path.exists(dest_dir))


if __name__ == "__main__":
    unittest.main()
