import os
import shutil
from modules.llm_interface import LLMInterface


class FileOrganizer:
    def __init__(
        self,
        repo_id,
        task,
        sample_files_dir="data/sample_files",
        categories_dir="data/categories",
    ):
        self.sample_files_dir = sample_files_dir
        self.categories_dir = categories_dir
        self.llm_interface = LLMInterface(repo_id, task)

    def create_sample_files(self):
        for item in os.listdir(self.sample_files_dir):
            item_path = os.path.join(self.sample_files_dir, item)
            if os.path.isfile(item_path):
                os.unlink(item_path)

        sample_files = [
            ("quarterly_report_Q1.pdf", "finance"),
            ("balance_sheet.xlsx", "finance"),
            ("annual_budget_2025.xlsx", "finance"),
            ("expense_report_march.pdf", "finance"),
            ("tax_documentation.pdf", "finance"),
            ("employee_policy.docx", "hr"),
            ("leave_form.pdf", "hr"),
            ("onboarding_checklist.docx", "hr"),
            ("performance_review_template.docx", "hr"),
            ("benefits_overview.pdf", "hr"),
        ]

        for filename, _ in sample_files:
            file_path = os.path.join(self.sample_files_dir, filename)
            with open(file_path, "w") as f:
                f.write(f"This is a sample file: {filename}")

        return True

    def list_files(self):
        return [
            f
            for f in os.listdir(self.sample_files_dir)
            if os.path.isfile(os.path.join(self.sample_files_dir, f))
        ]

    def organize_files(self):
        files = self.list_files()
        if not files:
            return None

        categories = self.llm_interface.categorize_files(files)

        for category in set(categories.values()):
            category_dir = os.path.join(self.categories_dir, category.lower())
            os.makedirs(category_dir, exist_ok=True)

        results = {}
        for filename, category in categories.items():
            category = category.lower()
            if category not in results:
                results[category] = []

            source = os.path.join(self.sample_files_dir, filename)
            destination = os.path.join(self.categories_dir, category, filename)

            if os.path.exists(source):
                shutil.move(source, destination)
                results[category].append(filename)

        return results
