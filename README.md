# 🤖 Corporate Companion Chatbot

A LangChain-based LLM-powered chatbot to assist employees with internal organizational tasks including personal data queries, meeting scheduling, and intelligent file organization.

---

## 📌 Features

### ✅ 1. User Information Collection
- Collects:
  - Name
  - Contact Details (Email, Phone)
  - Optional fields: Department, Employee ID, Office Location
  - Resume Upload (PDF)
- Handles missing data gracefully by storing placeholder values.
- Validates and parses phone numbers (India format) and emails.
- Allows users to query collected information.

### ✅ 2. Appointment Scheduling Assistant
- Schedules meetings:
  - With individual employees
  - With multiple employees
  - With entire teams
- Checks availability using:
  - `employee_schedules.csv` (booked slots)
  - `employee_teams.csv` (team membership)
- Respects:
  - Office hours (9 AM – 6 PM, Mon–Fri)
  - Lunch breaks (1 PM – 3 PM)
  - 1-hour availability rule
- Finds earliest valid slot for all participants.

### ✅ 3. Intelligent File Organizer
- Uses an LLM to:
  - Classify files (e.g., Finance, HR)
  - Create category folders
  - Move files accordingly
- Accepts both file names and content for classification.

---

## 🛠 Technologies Used

- **Python**
- **LangChain**
- **Streamlit** (UI)
- **Pydantic** (structured output parsing)
- **transformers / HuggingFace** (LLM backend)
- **dotenv** (for environment variable handling)
- **Pandas**, **os**, **shutil** (file & data handling)

---

## 📁 Project Structure

