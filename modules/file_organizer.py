import os
import shutil
from modules.llm_interface import LLMInterface

class FileOrganizer:
    def __init__(self, sample_files_dir="data/sample_files"):
        """Initialize the file organizer with a directory for sample files."""
        self.sample_files_dir = sample_files_dir
        self.llm_interface = LLMInterface()
        self._ensure_sample_dir()
    
    def _ensure_sample_dir(self):
        """Ensure the sample files directory exists."""
        os.makedirs(self.sample_files_dir, exist_ok=True)
    
    def create_sample_files(self):
        """Create sample files for categorization."""
        # Clear existing files
        for item in os.listdir(self.sample_files_dir):
            item_path = os.path.join(self.sample_files_dir, item)
            if os.path.isfile(item_path):
                os.unlink(item_path)
        
        # Define sample files with their categories
        sample_files = [
            # Finance category
            ("quarterly_report_Q1.pdf", "finance"),
            ("balance_sheet.xlsx", "finance"),
            ("annual_budget_2025.xlsx", "finance"),
            ("expense_report_march.pdf", "finance"),
            ("tax_documentation.pdf", "finance"),
            
            # HR category
            ("employee_policy.docx", "hr"),
            ("leave_form.pdf", "hr"),
            ("onboarding_checklist.docx", "hr"),
            ("performance_review_template.docx", "hr"),
            ("benefits_overview.pdf", "hr")
        ]
        
        # Create the files (empty files for demonstration)
        for filename, _ in sample_files:
            file_path = os.path.join(self.sample_files_dir, filename)
            with open(file_path, 'w') as f:
                f.write(f"This is a sample file: {filename}")
        
        return True
    
    def list_files(self):
        """List all files in the sample directory."""
        if not os.path.exists(self.sample_files_dir):
            return []
        
        return [f for f in os.listdir(self.sample_files_dir) 
                if os.path.isfile(os.path.join(self.sample_files_dir, f))]
    
    def organize_files(self):
        """Organize files into categories using LLM."""
        files = self.list_files()
        if not files:
            return None
        
        # Use LLM to categorize files
        categories = self.llm_interface.categorize_files(files)
        
        # Create category directories
        for category in set(categories.values()):
            category_dir = os.path.join(self.sample_files_dir, category.lower())
            os.makedirs(category_dir, exist_ok=True)
        
        # Move files to their categories
        results = {}
        for filename, category in categories.items():
            category = category.lower()
            if category not in results:
                results[category] = []
            
            source = os.path.join(self.sample_files_dir, filename)
            destination = os.path.join(self.sample_files_dir, category, filename)
            
            # Move the file
            if os.path.exists(source):
                shutil.move(source, destination)
                results[category].append(filename)
        
        return results