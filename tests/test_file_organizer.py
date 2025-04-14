import unittest
import os
import shutil
import tempfile
from modules.file_organizer import FileOrganizer

class TestFileOrganizer(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.file_organizer = FileOrganizer(sample_files_dir=self.test_dir)
    
    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_create_sample_files(self):
        # Create sample files
        result = self.file_organizer.create_sample_files()
        
        # Verify result
        self.assertTrue(result)
        
        # Verify files were created
        files = os.listdir(self.test_dir)
        self.assertGreater(len(files), 0)
        
        # Verify specific files exist
        self.assertIn("quarterly_report_Q1.pdf", files)
        self.assertIn("employee_policy.docx", files)
    
    def test_list_files(self):
        # Create some test files
        test_files = ["test1.txt", "test2.pdf", "test3.docx"]
        for file in test_files:
            with open(os.path.join(self.test_dir, file), 'w') as f:
                f.write(f"Test content for {file}")
        
        # List files
        files = self.file_organizer.list_files()
        
        # Verify all test files are listed
        for file in test_files:
            self.assertIn(file, files)
    
    def test_organize_files(self):
        # Create test files with clear categories
        test_files = {
            "budget_2025.xlsx": "finance",
            "employee_handbook.pdf": "hr"
        }
        
        for file, _ in test_files.items():
            with open(os.path.join(self.test_dir, file), 'w') as f:
                f.write(f"Test content for {file}")
        
        # Mock the LLM categorization
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
        
        # Replace the real method with mock
        original_method = self.file_organizer.llm_interface.categorize_files
        self.file_organizer.llm_interface.categorize_files = mock_categorize_files
        
        try:
            # Organize files
            results = self.file_organizer.organize_files()
            
            # Verify results
            self.assertIsNotNone(results)
            self.assertIn("finance", results)
            self.assertIn("hr", results)
            
            # Verify files were moved to correct directories
            for file, category in test_files.items():
                category_dir = os.path.join(self.test_dir, category)
                self.assertTrue(os.path.exists(os.path.join(category_dir, file)))
        
        finally:
            # Restore original method
            self.file_organizer.llm_interface.categorize_files = original_method

if __name__ == '__main__':
    unittest.main()