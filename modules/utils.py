import os
import json
import re
from datetime import datetime
import pandas as pd
import phonenumbers

def validate_email_format(email):
    """Validate email format using regex."""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))

def validate_phone_format(phone):
    """Validate phone number format using regex."""
    # Basic validation - can be expanded to support international formats
    phone_pattern = r'^\+?[0-9]{10,15}$'
    return bool(re.match(phone_pattern, phone))

def format_datetime(dt_str, input_format="%Y-%m-%d %H:%M", output_format="%B %d, %Y at %I:%M %p"):
    """Format datetime string from one format to another."""
    if not dt_str:
        return ""
    
    try:
        dt_obj = datetime.strptime(dt_str, input_format)
        return dt_obj.strftime(output_format)
    except ValueError:
        return dt_str

def load_json_safe(file_path, default=None):
    """Safely load JSON from a file, returning default if file doesn't exist."""
    if not os.path.exists(file_path):
        return default
    
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return default

def save_json_safe(data, file_path, indent=4):
    """Safely save data as JSON to a file."""
    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=indent)

def filter_dataframe(df, filters):
    """Apply filters to a DataFrame."""
    filtered_df = df.copy()
    
    for column, value in filters.items():
        if column in filtered_df.columns:
            filtered_df = filtered_df[filtered_df[column] == value]
    
    return filtered_df

def extract_date_components(date_str, date_format="%Y-%m-%d"):
    """Extract year, month, and day from a date string."""
    try:
        dt = datetime.strptime(date_str, date_format)
        return {
            "year": dt.year,
            "month": dt.month,
            "day": dt.day,
            "weekday": dt.weekday(),
            "weekday_name": dt.strftime("%A")
        }
    except ValueError:
        return None

def is_valid_slot(slot_time, work_hours=None):
    """Check if a time slot is within work hours."""
    if not work_hours:
        # Default work hours (9 AM - 6 PM)
        work_hours = {
            "start": datetime.strptime("09:00", "%H:%M").time(),
            "end": datetime.strptime("18:00", "%H:%M").time()
        }
    
    slot_dt = datetime.strptime(slot_time, "%H:%M")
    slot_t = slot_dt.time()
    
    return work_hours["start"] <= slot_t < work_hours["end"]

def calculate_time_difference(start_time, end_time, format="%H:%M"):
    """Calculate the difference between two time strings in hours."""
    start_dt = datetime.strptime(start_time, format)
    end_dt = datetime.strptime(end_time, format)
    
    difference = end_dt - start_dt
    hours = difference.total_seconds() / 3600
    
    return hours

def generate_time_slots(start_hour=9, end_hour=18, interval_minutes=30):
    """Generate time slots with a specific interval."""
    slots = []
    current_hour = start_hour
    current_minute = 0
    
    while current_hour < end_hour:
        time_str = f"{current_hour:02d}:{current_minute:02d}"
        slots.append(time_str)
        
        # Update time
        current_minute += interval_minutes
        if current_minute >= 60:
            current_hour += 1
            current_minute = 0
    
    return slots

def sanitize_text(value, default="Not provided"):
    value = value.strip() if value else ""
    return value if value else default

def normalize_phone(phone):
    try:
        parsed = phonenumbers.parse(phone, "IN")
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        else:
            return "Invalid number"
    except phonenumbers.NumberParseException:
        return "Invalid number"
    
  


