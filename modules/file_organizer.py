import os
import shutil
from modules.llm_interface import LLMInterface

class FileOrganizer:
    def __init__(self, sample_files_dir="data/sample_files"):
        """Initialize the file organizer with a directory for sample files."""
        self.sample_files_dir = sample_files_dir
        self.llm_interface = LLMInterface()
   
    def list_files(self):
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