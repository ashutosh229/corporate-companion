import os
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from modules.user_manager import UserManager
from modules.meeting_scheduler import MeetingScheduler
from modules.file_organizer import FileOrganizer
from modules.llm_interface import LLMInterface
from modules.utils import sanitize_text, normalize_phone

load_dotenv()

repo_id = os.getenv("REPO_ID")
task = os.getenv("TASK")
teams_file = os.getenv("TEAMS_FILE")
schedule_file = os.getenv("SCHEDULE_FILE")
sample_files_dir = os.getenv("SAMPLE_FILES_DIR")
file_categories_dir = os.getenv("FILE_CATEGORIES_DIR")
hugging_face_token = os.getenv("HUGGING_FACE_TOKEN")
model_kwargs = {"temperature": 0.5, "top_p": 0.95, "max_length": 512}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_task" not in st.session_state:
    st.session_state.current_task = "intro"
if "user_info_collected" not in st.session_state:
    st.session_state.user_info_collected = False
if "upload_resume" not in st.session_state:
    st.session_state.upload_resume = False
if "employee_id" not in st.session_state:
    st.session_state.employee_id = ""

user_manager = UserManager()
llm_interface = LLMInterface(
    repo_id,
    task,
    model_kwargs,
    hugging_face_token,
)
scheduler = MeetingScheduler(teams_file, schedule_file)
file_organizer = FileOrganizer(
    repo_id,
    task,
    sample_files_dir,
    file_categories_dir,
    model_kwargs,
    hugging_face_token,
)

st.title("Corporate Companion")
st.subheader("Your AI-powered Employee Assistant")

with st.sidebar:
    st.header("Navigation")
    task = st.radio(
        "Select a task",
        ["User Information", "Meeting Scheduler", "File Organizer", "HR Assistance"],
    )

    if task == "User Information":
        st.session_state.current_task = "user_info"
    elif task == "Meeting Scheduler":
        st.session_state.current_task = "scheduler"
    elif task == "File Organizer":
        st.session_state.current_task = "file_organizer"
    elif task == "HR Assistance":
        st.session_state.current_task = "hr_assistance"

    st.divider()
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.experimental_rerun()

if (
    st.session_state.current_task == "intro"
    or st.session_state.current_task == "user_info"
):
    if not st.session_state.get("user_info_collected", False):
        st.write("Welcome! Let's start by collecting some basic information.")

        st.subheader("Employee Identification")
        employee_id = st.text_input("Employee ID (Required)", key="employee_id_input")

        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name", key="name_input")

        with col2:
            email = st.text_input("Email", key="email_input")
            phone = st.text_input("Phone Number", key="phone_input")

        with st.expander("Additional Information (Optional)"):
            department = st.text_input("Department", key="department_input")
            office_location = st.text_input(
                "Office Location", key="office_location_input"
            )

        resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

        if st.button("Submit Information"):
            if not employee_id.strip():
                st.error("Employee ID is required")
            else:
                validation_results = user_manager.validate_user_info(name, email, phone)
                if validation_results["valid"]:
                    user_data = {
                        "name": sanitize_text(name, default="Anonymous User"),
                        "email": sanitize_text(email),
                        "phone": normalize_phone(phone),
                        "department": sanitize_text(department),
                        "employee_id": employee_id,
                        "office_location": sanitize_text(office_location),
                        "has_resume": resume_file is not None,
                    }
                    if resume_file:
                        user_manager.save_resume(resume_file, employee_id)

                    user_manager.save_user_data(user_data)

                    st.session_state.user_info_collected = True
                    st.session_state.employee_id = employee_id
                    st.success("Information saved successfully!")
                    st.experimental_rerun()
                else:
                    for field, message in validation_results["errors"].items():
                        if message:
                            st.error(f"{field}: {message}")
    else:
        employee_id = st.session_state.get("employee_id", "")
        user_data = user_manager.get_user_data(user_identifier=employee_id)
        if user_data:
            st.write(f"### Welcome, {user_data.get('name', 'User')}!")

            col1, col2 = st.columns(2)
            with col1:
                st.write("**Contact Information**")
                st.write(f"Email: {user_data.get('email', 'Not provided')}")
                st.write(f"Phone: {user_data.get('phone', 'Not provided')}")

            with col2:
                st.write("**Employment Details**")
                st.write(f"Department: {user_data.get('department', 'Not provided')}")
                st.write(f"Employee ID: {user_data.get('employee_id', 'Not provided')}")
                st.write(
                    f"Office Location: {user_data.get('office_location', 'Not provided')}"
                )

            if user_data.get("has_resume", False):
                st.write("Resume: Uploaded ✓")
            else:
                st.write("Resume: Not uploaded")

            if st.button("Update Information"):
                st.session_state.user_info_collected = False
                st.experimental_rerun()

elif st.session_state.current_task == "scheduler":
    st.header("Meeting Scheduler")

    meeting_type = st.radio(
        "Schedule meeting with:",
        ["Individual Employee", "Multiple Employees", "Entire Team"],
    )

    if meeting_type == "Individual Employee":
        employee = st.selectbox("Select employee:", scheduler.get_all_employees())
        participants = [employee]
    elif meeting_type == "Multiple Employees":
        participants = st.multiselect(
            "Select employees:", scheduler.get_all_employees()
        )
    else:
        team = st.selectbox("Select team:", scheduler.get_all_teams())
        participants = scheduler.get_team_members(team)
        st.write(f"Team members: {', '.join(participants)}")

    duration = st.number_input(
        "Meeting duration (hours):", min_value=0.5, max_value=3.0, value=1.0, step=0.5
    )

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start looking from date:")
    with col2:
        days_to_search = st.number_input(
            "Number of days to search:", min_value=1, max_value=14, value=5, step=1
        )

    if st.button("Find Available Slots"):
        if participants:
            with st.spinner("Finding available slots..."):
                available_slots = scheduler.find_available_slots(
                    participants, duration, start_date, days_to_search
                )

                if available_slots:
                    st.success(f"Found {len(available_slots)} available slots!")

                    slots_container = st.container()

                    st.markdown(
                        """
                        <style>
                        .scrollable-slots-container {
                            max-height: 400px;
                            overflow-y: scroll;
                            padding-right: 10px;
                        }

                        .slot-entry {
                            padding: 10px;
                            margin-bottom: 8px;
                            border: 1px solid #e0e0e0;
                            border-radius: 5px;
                            background-color: #f9f9f9;
                        }
                        </style>
                    """,
                        unsafe_allow_html=True,
                    )

                    with slots_container:
                        st.markdown(
                            '<div class="scrollable-slots-container">',
                            unsafe_allow_html=True,
                        )

                        for i, slot in enumerate(available_slots, 1):
                            slot_date = slot["date"]
                            day_of_week = datetime.strptime(
                                slot_date, "%Y-%m-%d"
                            ).strftime("%A")
                            slot_str = f"{slot_date} ({day_of_week}) from {slot['start_time']} to {slot['end_time']}"

                            slot_key = f"slot_{slot_date}_{slot['start_time'].replace(':', '')}"

                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"**Slot {i}:** {slot_str}")
                            with col2:
                                if st.button("Book", key=f"book_{slot_key}"):
                                    scheduler.book_meeting(participants, slot)
                                    st.success(
                                        f"Meeting booked for {slot_str} with {', '.join(participants)}!"
                                    )
                                    st.balloons()

                            st.markdown("</div>", unsafe_allow_html=True)

                        st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.error("No available slots found in the specified date range.")
        else:
            st.warning("Please select at least one participant.")

elif st.session_state.current_task == "file_organizer":
    st.header("Intelligent File Organizer")

    files = file_organizer.list_files()
    if files:
        st.write("### Current Files:")
        for file in files:
            st.write(f"- {file}")

    if st.button("Organize Files"):
        with st.spinner("Analyzing and organizing files..."):
            results = file_organizer.organize_files()

            if results:
                st.success("Files organized successfully!")

                for category, files in results.items():
                    st.write(f"**{category.title()}** category:")
                    for file in files:
                        st.write(f"- {file}")
            else:
                st.error("Error organizing files. Please try again.")

elif st.session_state.current_task == "hr_assistance":
    st.header("HR Policy Assistant")

    user_query = st.text_input(
        "Ask a question about HR policies, upcoming events, or company information:"
    )

    if user_query:
        st.session_state.chat_history.append({"role": "user", "content": user_query})

        with st.spinner("Processing..."):
            response = llm_interface.process_hr_query(user_query)
            st.session_state.chat_history.append(
                {"role": "assistant", "content": response}
            )

    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.write(f"**You:** {message['content']}")
        else:
            st.write(f"**Assistant:** {message['content']}")

st.divider()
st.caption("Corporate Companion | Developed by Ashutosh Kumar Jha")
