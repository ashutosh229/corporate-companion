# 🤖 Corporate Companion Chatbot

A LangChain-based LLM-powered chatbot to assist employees with internal organizational tasks including personal data feeding and querying, meeting scheduling, and intelligent file organization and other core functionalities.

---

## 📌 Features

### ✅ 1. User Information Collection
- Collects:
  - Employee ID (Unique identifier for employees)
  - Name
  - Contact Details (Email, Phone)
  - Optional fields: Department, Office Location
  - Resume (PDF)
- Handles missing data gracefully by storing placeholder values.
- Validates critical details like emails and phone numbers
- Parsing of phone numbers (India format) and emails into proper structure for storage purposes.
<!-- - Allows users to query collected information. -->

### ✅ 2. Appointment Scheduling Assistant
- Schedules meetings:
  - With individual employees
  - With multiple employees
  - With entire teams
- Checks availability using data files:
  - `employee_schedules.csv` (booked slots)
  - `employee_teams.csv` (team membership)
- Considers the following aspects:
  - Office hours (9 AM – 6 PM, Mon–Fri) should be considered for meetings
  - Lunch breaks (1 PM – 3 PM) should not be considered
  - 1-hour unavailability rule i.e. if the booked slot is for 10:00 AM, then the person will be unavailable for the next 1 hour
- Finds earliest valid time slot for all participants.

### ✅ 3. Intelligent File Organizer
- Uses an LLM to:
  - Classify available files into categories (e.g., Finance, HR)
  - Create category folders
  - Move files accordingly
- Categorizes based on the name of the file (can be extended to checking of file content as well).

### ✅ 4. HR Policy Assistant
- Answers the queries of the users related to the HR policies and holidays 
- Showing up of upcoming events on being asked by the user
- The data like policies, holidays information, events, etc. is hardcoded in the file (later on, can be extended to the functionality of being fetched from the database)
-In production level, the data will be stored somewhere else and will be fetched into the LLM for answering purposes. 

---

## 🛠 Technologies Used

- **Python**
- **LangChain**
- **Streamlit** (UI)
- **Pydantic** (structured output parsing)
- **transformers / HuggingFace** (LLM backend)
- **dotenv** (for environment variable handling)
- **Pandas**, **os**, **shutil**, **json** (file & data handling, data loading)
- **typing** (for type annotations)
- **datetime** (for date-time handling and manipulations)
- **re**, **phonenumbers**, **email_validator** (for validation purposes)



## 📁 Project Structure

📦 corporate-companion
├── .git
├── .gitignore
├── README.md
├── app.py
├── data
│   ├── categories
│   ├── employee_schedules.csv
│   ├── employee_teams.csv
│   ├── sample_files
│   └── user_data
│       └── resumes
├── modules
│   ├── __init__.py
│   ├── file_organizer.py
│   ├── llm_interface.py
│   ├── meeting_scheduler.py
│   ├── user_manager.py
│   └── utils.py
├── requirements.txt

