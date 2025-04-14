import unittest
import os
import shutil
import tempfile
from modules.user_manager import UserManager

class TestUserManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.user_manager = UserManager(data_dir=self.test_dir)
    
    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_validate_user_info(self):
        # Test valid information
        result = self.user_manager.validate_user_info(
            "John Doe", 
            "john.doe@example.com", 
            "+1234567890"
        )
        self.assertTrue(result["valid"])
        
        # Test invalid email
        result = self.user_manager.validate_user_info(
            "John Doe", 
            "invalid-email", 
            "+1234567890"
        )
        self.assertFalse(result["valid"])
        self.assertIn("email", result["errors"])
        
        # Test invalid phone
        result = self.user_manager.validate_user_info(
            "John Doe", 
            "john.doe@example.com", 
            "not-a-phone"
        )
        self.assertFalse(result["valid"])
        self.assertIn("phone", result["errors"])
    
    def test_save_and_get_user_data(self):
        # Test saving user data
        user_data = {
            "name": "Jane Smith",
            "email": "jane.smith@example.com",
            "phone": "+9876543210",
            "department": "Engineering"
        }
        
        self.user_manager.save_user_data(user_data)
        
        # Test getting user data
        retrieved_data = self.user_manager.get_user_data("Jane Smith")
        
        self.assertEqual(retrieved_data["name"], user_data["name"])
        self.assertEqual(retrieved_data["email"], user_data["email"])
        self.assertEqual(retrieved_data["phone"], user_data["phone"])
        self.assertEqual(retrieved_data["department"], user_data["department"])

if __name__ == '__main__':
    unittest.main()