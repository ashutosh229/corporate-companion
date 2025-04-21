import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
import calendar
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel


class MeetingSlot(BaseModel):
    date: str
    start_time: str
    end_time: str
    duration: float
    participants: List[str]


class MeetingScheduler:
    def __init__(
        self, teams_file="employee_teams.csv", schedules_file="employee_schedules.csv"
    ):
        self.teams_file = teams_file
        self.schedules_file = schedules_file

        self.employee_teams = pd.read_csv(self.teams_file)

        self.employee_schedules = pd.read_csv(self.schedules_file, index_col=0)
        self.process_schedules()

        self.work_start = time(9, 0)
        self.work_end = time(18, 0)
        self.lunch_start = time(13, 0)
        self.lunch_end = time(15, 0)

        self.work_days = [0, 1, 2, 3, 4]

    def process_schedules(self):
        self.booked_slots = {}

        for employee, row in self.employee_schedules.iterrows():
            self.booked_slots[employee] = {}

            for date_col in self.employee_schedules.columns:
                if pd.notna(row[date_col]):
                    time_slots = row[date_col].split(",")
                    time_slots = [slot.strip() for slot in time_slots]

                    self.booked_slots[employee][date_col] = time_slots

    def get_all_employees(self) -> List[str]:
        return sorted(self.employee_teams["Employee"].tolist())

    def get_all_teams(self) -> List[str]:
        return sorted(self.employee_teams["Team"].unique().tolist())

    def get_team_members(self, team_name: str) -> List[str]:
        team_df = self.employee_teams[self.employee_teams["Team"] == team_name]
        return team_df["Employee"].tolist()

    def is_available(self, employee: str, date_str: str, time_str: str) -> bool:
        hour, minute = map(int, time_str.split(":"))
        time_str = f"{hour:02d}:{minute:02d}"

        if (
            employee not in self.booked_slots
            or date_str not in self.booked_slots[employee]
        ):
            return True

        if time_str in self.booked_slots[employee][date_str]:
            return False

        dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        prev_hour = dt - timedelta(hours=1)
        prev_date_str = prev_hour.strftime("%Y-%m-%d")
        prev_time_str = prev_hour.strftime("%H:%M")

        if (
            prev_date_str == date_str
            and employee in self.booked_slots
            and prev_date_str in self.booked_slots[employee]
            and prev_time_str in self.booked_slots[employee][prev_date_str]
        ):
            return False

        return True

    def find_available_slots(
        self,
        participants: List[str],
        duration: float = 1.0,
        start_date=None,
        days_ahead: int = 10,
    ) -> List[Dict]:
        if not participants:
            return []

        expanded_participants = []
        for p in participants:
            if p in self.get_all_teams():
                expanded_participants.extend(self.get_team_members(p))
            else:
                expanded_participants.append(p)

        participants = list(set(expanded_participants))

        if start_date is None:
            start_date = datetime.now().date()
        elif isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()

        available_slots = []
        hours_needed = int(duration)

        for day_offset in range(days_ahead):
            current_date = start_date + timedelta(days=day_offset)

            if current_date.weekday() not in self.work_days:
                continue

            date_str = current_date.strftime("%Y-%m-%d")

            for hour in range(9, 18 - hours_needed + 1):
                time_str = f"{hour:02d}:00"

                current_time = time(hour, 0)
                if self.lunch_start <= current_time < self.lunch_end:
                    continue

                all_available = True

                for p in participants:
                    for h in range(hours_needed):
                        check_time = time(hour + h, 0)

                        if self.lunch_start <= check_time < self.lunch_end:
                            all_available = False
                            break

                        check_time_str = f"{(hour + h):02d}:00"

                        if not self.is_available(p, date_str, check_time_str):
                            all_available = False
                            break

                    if not all_available:
                        break

                if all_available:
                    end_hour = hour + hours_needed
                    end_time = f"{end_hour:02d}:00"

                    available_slot = {
                        "date": date_str,
                        "start_time": time_str,
                        "end_time": end_time,
                        "duration": duration,
                        "participants": participants,
                    }

                    available_slots.append(available_slot)

        return available_slots

    def book_meeting(self, participants: List[str], slot: Dict[str, Any]) -> bool:
        try:
            start_dt = datetime.strptime(
                f"{slot['date']} {slot['start_time']}", "%Y-%m-%d %H:%M"
            )
            end_dt = datetime.strptime(
                f"{slot['date']} {slot['end_time']}", "%Y-%m-%d %H:%M"
            )
        except ValueError:
            return False

        date_str = slot["date"]
        current_dt = start_dt

        while current_dt < end_dt:
            time_str = current_dt.strftime("%H:%M")

            for participant in participants:
                if participant not in self.booked_slots:
                    self.booked_slots[participant] = {}

                if date_str not in self.booked_slots[participant]:
                    self.booked_slots[participant][date_str] = []

                self.booked_slots[participant][date_str].append(time_str)

            current_dt += timedelta(hours=1)

        self.save_schedules()

        return True

    def save_schedules(self):
        new_data = {}

        for employee, dates in self.booked_slots.items():
            new_data[employee] = {}
            for date, times in dates.items():
                sorted_times = sorted(times)
                new_data[employee][date] = ", ".join(sorted_times)

        result_df = pd.DataFrame.from_dict(new_data, orient="index")

        for col in self.employee_schedules.columns:
            if col not in result_df.columns:
                result_df[col] = ""

        result_df = result_df[self.employee_schedules.columns]

        result_df.to_csv(self.schedules_file)

        return True
