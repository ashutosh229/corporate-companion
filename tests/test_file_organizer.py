import unittest
import os
import shutil
import tempfile
from modules.file_organizer import FileOrganizer


class TestFileOrganizer(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.file_organizer = FileOrganizer(sample_files_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_create_sample_files(self):
        result = self.file_organizer.create_sample_files()

        self.assertTrue(result)

        files = os.listdir(self.test_dir)
        self.assertGreater(len(files), 0)

        self.assertIn("quarterly_report_Q1.pdf", files)
        self.assertIn("employee_policy.docx", files)

    def test_list_files(self):
        test_files = ["test1.txt", "test2.pdf", "test3.docx"]
        for file in test_files:
            with open(os.path.join(self.test_dir, file), "w") as f:
                f.write(f"Test content for {file}")

        files = self.file_organizer.list_files()

        for file in test_files:
            self.assertIn(file, files)

    def test_organize_files(self):
        test_files = {"budget_2025.xlsx": "finance", "employee_handbook.pdf": "hr"}

        for file, _ in test_files.items():
            with open(os.path.join(self.test_dir, file), "w") as f:
                f.write(f"Test content for {file}")

        def mock_categorize_files(files):
            categories = {}
            for file in files:
                if "budget" in file.lower():
                    categories[file] = "finance"
                elif "employee" in file.lower():
                    categories[file] = "hr"
                else:
                    categories[file] = "other"
            return categories

        original_method = self.file_organizer.llm_interface.categorize_files
        self.file_organizer.llm_interface.categorize_files = mock_categorize_files

        try:
            results = self.file_organizer.organize_files()

            self.assertIsNotNone(results)
            self.assertIn("finance", results)
            self.assertIn("hr", results)

            for file, category in test_files.items():
                category_dir = os.path.join(self.test_dir, category)
                self.assertTrue(os.path.exists(os.path.join(category_dir, file)))

        finally:
            self.file_organizer.llm_interface.categorize_files = original_method


if __name__ == "__main__":
    unittest.main()
