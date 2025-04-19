import os
import json
import re
import phonenumbers
from email_validator import validate_email, EmailNotValidError
import PyPDF2
from datetime import datetime

class UserManager:
    def __init__(self, data_dir="data/user_data"):
        """Initialize the UserManager with a directory for storing user data."""
        self.data_dir = data_dir
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """Ensure the data directory exists."""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, "resumes"), exist_ok=True)
    
    def validate_user_info(self, name, email, phone):
        """Validate user information."""
        errors = {"name": "", "email": "", "phone": ""}
        is_valid = True
        
        # Validate name (optional but if provided should be valid)
        if name and not re.match(r"^[A-Za-z\s\-'\.]{2,50}$", name):
            errors["name"] = "Name should contain only letters, spaces, hyphens, apostrophes, and periods (2-50 chars)."
            is_valid = False
        
        # Validate email (optional but if provided should be valid)
        if email:
            try:
                validate_email(email)
            except EmailNotValidError as e:
                errors["email"] = str(e)
                is_valid = False
        
        # Validate phone (optional but if provided should be valid)
        if phone:
            try:
                parsed_number = phonenumbers.parse(phone, "IN")  # Default to US, could be made configurable
                if not phonenumbers.is_valid_number(parsed_number):
                    errors["phone"] = "Invalid phone number format."
                    is_valid = False
            except Exception:
                errors["phone"] = "Invalid phone number format."
                is_valid = False
        
        return {
            "valid": is_valid,
            "errors": errors
        }
    
    def save_user_data(self, user_data):        
        # Use name or a timestamp as identifier
        identifier = user_data.get("employee_id")
        file_path = os.path.join(self.data_dir, f"{identifier}.json")
        
        with open(file_path, 'w') as f:
            json.dump(user_data, f, indent=4)
        
        return True
    
    def get_user_data(self, user_identifier):
        user_file = f"{user_identifier}.json"
        file_path = os.path.join(self.data_dir, user_file)
        
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        
        return None
    
    def save_resume(self, resume_file, employee_id):        
        # Create a sanitized filename
        safe_name = employee_id
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{safe_name}_{timestamp}.pdf"
        file_path = os.path.join(self.data_dir, "resumes", filename)
        
        # Save the file
        with open(file_path, "wb") as f:
            f.write(resume_file.getvalue())
        
        return file_path
    
    def extract_resume_text(self, resume_path):
        """Extract text from a resume PDF file."""
        try:
            reader = PyPDF2.PdfReader(resume_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error extracting resume text: {e}")
            return ""