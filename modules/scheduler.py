import os
import pandas as pd
from datetime import datetime, timedelta, time
import calendar

class MeetingScheduler:
    def __init__(self, teams_file="data/employee_teams.csv", schedules_file="data/employee_schedules.csv"):
        """Initialize the meeting scheduler with employee team and schedule data."""
        self.teams_file = teams_file
        self.schedules_file = schedules_file
        
        # Ensure data files exist (create with sample data if they don't)
        self._ensure_data_files()
        
        # Load employee data
        self.employee_teams = pd.read_csv(self.teams_file)
        self.employee_schedules = pd.read_csv(self.schedules_file)
        
        # Office hours
        self.work_start = time(9, 0)  # 9:00 AM
        self.work_end = time(18, 0)   # 6:00 PM
        self.lunch_start = time(13, 0)  # 1:00 PM
        self.lunch_end = time(15, 0)    # 3:00 PM
        
        # Available work days
        self.work_days = [0, 1, 2, 3, 4]  # Monday to Friday (0-4)
    
    def _ensure_data_files(self):
        """Create sample data files if they don't exist."""
        os.makedirs(os.path.dirname(self.teams_file), exist_ok=True)
        
        # Create employee teams file if it doesn't exist
        if not os.path.exists(self.teams_file):
            teams_data = {
                "employee_name": [
                    "John Smith", "Emily Johnson", "Michael Brown", "Sarah Davis", 
                    "David Wilson", "Jennifer Miller", "Robert Taylor", "Linda Anderson",
                    "William Thomas", "Elizabeth Jackson"
                ],
                "team": [
                    "Engineering", "Marketing", "Engineering", "HR", 
                    "Sales", "Marketing", "Engineering", "HR",
                    "Sales", "Finance"
                ]
            }
            pd.DataFrame(teams_data).to_csv(self.teams_file, index=False)
        
        # Create employee schedules file if it doesn't exist
        if not os.path.exists(self.schedules_file):
            # Generate some sample appointments for April 2025
            schedules_data = {
                "employee_name": [],
                "date": [],
                "time": []
            }
            
            employees = ["John Smith", "Emily Johnson", "Michael Brown", "Sarah Davis", 
                        "David Wilson", "Jennifer Miller", "Robert Taylor", "Linda Anderson",
                        "William Thomas", "Elizabeth Jackson"]
            
            # Generate some random meetings for April 2025
            for day in range(1, 31):
                # Skip weekends
                weekday = calendar.weekday(2025, 4, day)
                if weekday >= 5:  # Saturday or Sunday
                    continue
                
                for hour in [9, 10, 11, 13, 14, 15, 16, 17]:
                    # Add meetings for some employees
                    for emp_idx in range(len(employees)):
                        # Skip some slots to ensure availability
                        if (day + hour + emp_idx) % 5 != 0:
                            continue
                        
                        schedules_data["employee_name"].append(employees[emp_idx])
                        schedules_data["date"].append(f"2025-04-{day:02d}")
                        schedules_data["time"].append(f"{hour:02d}:00")
            
            pd.DataFrame(schedules_data).to_csv(self.schedules_file, index=False)
    
    def get_all_employees(self):
        """Get a list of all employees."""
        return sorted(self.employee_teams["employee_name"].unique().tolist())
    
    def get_all_teams(self):
        """Get a list of all teams."""
        return sorted(self.employee_teams["team"].unique().tolist())
    
    def get_team_members(self, team_name):
        """Get all members of a specific team."""
        team_df = self.employee_teams[self.employee_teams["team"] == team_name]
        return team_df["employee_name"].tolist()
    
    def is_available(self, employee, date_str, time_str):
        """Check if an employee is available at a specific date and time."""
        # Check if there's a direct scheduling conflict
        conflict = self.employee_schedules[
            (self.employee_schedules["employee_name"] == employee) &
            (self.employee_schedules["date"] == date_str) &
            (self.employee_schedules["time"] == time_str)
        ]
        
        if not conflict.empty:
            return False
        
        # Check if there's a meeting in the previous hour (which would block this hour)
        dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        prev_hour = dt - timedelta(hours=1)
        prev_date_str = prev_hour.strftime("%Y-%m-%d")
        prev_time_str = prev_hour.strftime("%H:%M")
        
        prev_conflict = self.employee_schedules[
            (self.employee_schedules["employee_name"] == employee) &
            (self.employee_schedules["date"] == prev_date_str) &
            (self.employee_schedules["time"] == prev_time_str)
        ]
        
        return prev_conflict.empty
    
    def find_available_slots(self, participants, duration=1.0, start_date=None, days_ahead=5):
        """Find available meeting slots for the given participants."""
        if not participants:
            return []
        
        # Set default start date to today if not provided
        if start_date is None:
            start_date = datetime.now().date()
        elif isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        
        available_slots = []
        hours_needed = int(duration * 2)  # Convert to half-hour slots
        
        # Loop through the requested number of days
        for day_offset in range(days_ahead):
            current_date = start_date + timedelta(days=day_offset)
            
            # Skip weekends
            if current_date.weekday() not in self.work_days:
                continue
            
            date_str = current_date.strftime("%Y-%m-%d")
            
            # Check each hour during work hours
            for hour in range(9, 18):  # 9 AM to 5 PM (5 PM + 1 hour meeting ends at 6 PM)
                for minute in [0, 30]:  # Check half-hour slots
                    # Skip lunch hours
                    current_time = time(hour, minute)
                    if self.lunch_start <= current_time < self.lunch_end:
                        continue
                    
                    time_str = f"{hour:02d}:{minute:02d}"
                    
                    # Check if all participants are available for the duration
                    all_available = True
                    
                    # Check availability for the whole duration
                    for p in participants:
                        slot_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                        
                        # Check each half-hour in the duration
                        for i in range(hours_needed):
                            check_time = slot_time + timedelta(minutes=30 * i)
                            
                            # Skip if outside work hours
                            if check_time.time() < self.work_start or check_time.time() >= self.work_end:
                                all_available = False
                                break
                            
                            # Skip lunch hours
                            if self.lunch_start <= check_time.time() < self.lunch_end:
                                all_available = False
                                break
                            
                            check_date_str = check_time.strftime("%Y-%m-%d")
                            check_time_str = check_time.strftime("%H:%M")
                            
                            if not self.is_available(p, check_date_str, check_time_str):
                                all_available = False
                                break
                        
                        if not all_available:
                            break
                    
                    if all_available:
                        # Calculate end time
                        end_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M") + timedelta(hours=duration)
                        
                        available_slots.append({
                            "date": date_str,
                            "start_time": time_str,
                            "end_time": end_time.strftime("%H:%M"),
                            "duration": duration,
                            "participants": participants
                        })
        
        return available_slots
    
    def book_meeting(self, participants, slot):
        """Book a meeting for the participants."""
        new_bookings = []
        
        # Convert slot to datetime for manipulation
        start_dt = datetime.strptime(f"{slot['date']} {slot['start_time']}", "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(f"{slot['date']} {slot['end_time']}", "%Y-%m-%d %H:%M")
        
        # Create 1-hour blocks for booking
        current_dt = start_dt
        while current_dt < end_dt:
            current_date = current_dt.strftime("%Y-%m-%d")
            current_time = current_dt.strftime("%H:%M")
            
            # Add booking for each participant
            for participant in participants:
                new_bookings.append({
                    "employee_name": participant,
                    "date": current_date,
                    "time": current_time
                })
            
            # Move to next hour
            current_dt += timedelta(hours=1)
        
        # Add new bookings to the schedule
        new_bookings_df = pd.DataFrame(new_bookings)
        self.employee_schedules = pd.concat([self.employee_schedules, new_bookings_df], ignore_index=True)
        
        # Save updated schedules
        self.employee_schedules.to_csv(self.schedules_file, index=False)
        
        return True