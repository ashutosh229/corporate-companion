import unittest
import os
import pandas as pd
import tempfile
from datetime import datetime, timedelta
from modules.scheduler import MeetingScheduler

class TestMeetingScheduler(unittest.TestCase):
    def setUp(self):
        # Create temporary files for testing
        self.test_teams_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        self.test_schedules_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        
        # Create test data
        teams_data = pd.DataFrame({
            "employee_name": ["Test User 1", "Test User 2", "Test User 3"],
            "team": ["Test Team A", "Test Team A", "Test Team B"]
        })
        
        schedules_data = pd.DataFrame({
            "employee_name": ["Test User 1", "Test User 2"],
            "date": ["2025-04-15", "2025-04-15"],
            "time": ["10:00", "14:00"]
        })
        
        # Save test data to files
        teams_data.to_csv(self.test_teams_file.name, index=False)
        schedules_data.to_csv(self.test_schedules_file.name, index=False)
        
        # Initialize scheduler with test files
        self.scheduler = MeetingScheduler(
            teams_file=self.test_teams_file.name,
            schedules_file=self.test_schedules_file.name
        )
    
    def tearDown(self):
        # Remove temporary files
        os.unlink(self.test_teams_file.name)
        os.unlink(self.test_schedules_file.name)
    
    def test_get_all_employees(self):
        employees = self.scheduler.get_all_employees()
        self.assertEqual(len(employees), 3)
        self.assertIn("Test User 1", employees)
        self.assertIn("Test User 2", employees)
        self.assertIn("Test User 3", employees)
    
    def test_get_all_teams(self):
        teams = self.scheduler.get_all_teams()
        self.assertEqual(len(teams), 2)
        self.assertIn("Test Team A", teams)
        self.assertIn("Test Team B", teams)
    
    def test_get_team_members(self):
        team_a_members = self.scheduler.get_team_members("Test Team A")
        self.assertEqual(len(team_a_members), 2)
        self.assertIn("Test User 1", team_a_members)
        self.assertIn("Test User 2", team_a_members)
        
        team_b_members = self.scheduler.get_team_members("Test Team B")
        self.assertEqual(len(team_b_members), 1)
        self.assertIn("Test User 3", team_b_members)
    
    def test_is_available(self):
        # User 1 is not available at 10:00
        self.assertFalse(self.scheduler.is_available("Test User 1", "2025-04-15", "10:00"))
        
        # User 1 is not available at 11:00 (blocked by 10:00 meeting)
        self.assertFalse(self.scheduler.is_available("Test User 1", "2025-04-15", "11:00"))
        
        # User 1 is available at 12:00
        self.assertTrue(self.scheduler.is_available("Test User 1", "2025-04-15", "12:00"))
        
        # User 3 is available (no schedule entries)
        self.assertTrue(self.scheduler.is_available("Test User 3", "2025-04-15", "10:00"))
    
    def test_find_available_slots(self):
        # Find slots for User 3 (who has no schedule entries)
        start_date = datetime(2025, 4, 15).date()
        slots = self.scheduler.find_available_slots(["Test User 3"], 1.0, start_date, 1)
        
        # Should have multiple available slots on a workday
        self.assertGreater(len(slots), 0)
        
        # Test with multiple users with conflicts
        slots = self.scheduler.find_available_slots(
            ["Test User 1", "Test User 2"], 
            1.0, 
            start_date, 
            1
        )
        
        # Verify each slot works for both users
        for slot in slots:
            self.assertTrue(
                self.scheduler.is_available("Test User 1", slot["date"], slot["start_time"]) and
                self.scheduler.is_available("Test User 2", slot["date"], slot["start_time"])
            )

if __name__ == '__main__':
    unittest.main()