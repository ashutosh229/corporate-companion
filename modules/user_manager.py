import os
import json
import re
import phonenumbers
from email_validator import validate_email, EmailNotValidError
import PyPDF2
from datetime import datetime

class UserManager:
    def __init__(self, data_dir="data/user_data"):
        self.data_dir = data_dir
    
    
    def validate_user_info(self, name, email, phone):
        errors = {"name": "", "email": "", "phone": ""}
        is_valid = True
        
        if name and not re.match(r"^[A-Za-z\s\-'\.]{2,50}$", name):
            errors["name"] = "Name should contain only letters, spaces, hyphens, apostrophes, and periods (2-50 chars)."
            is_valid = False
        
        if email:
            try:
                validate_email(email)
            except EmailNotValidError as e:
                errors["email"] = str(e)
                is_valid = False
        
        if phone:
            try:
                parsed_number = phonenumbers.parse(phone, "IN")
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
        safe_name = employee_id
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{safe_name}_{timestamp}.pdf"
        file_path = os.path.join(self.data_dir, "resumes", filename)
        
        with open(file_path, "wb") as f:
            f.write(resume_file.getvalue())
        
        return file_path
    
    def extract_resume_text(self, resume_path):
        try:
            reader = PyPDF2.PdfReader(resume_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error extracting resume text: {e}")
            return ""