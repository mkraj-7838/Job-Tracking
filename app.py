# 1_💼_Job_Tracker.py

import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil import parser
import google.generativeai as genai
import json
import firebase_admin
from firebase_admin import credentials, firestore
import re

# -------------------------
# CONFIG
# -------------------------
# Updated columns to include new status and round tracking fields
EXPECTED_COLS = [
    "Company Name", "Offer Type", "Stipend", "CTC", "Eligibility", "Branches",
    "Role", "Recruitment Process", "Application Deadline", "Form Link",
    "POC Name", "POC Phone", "Date Added",
    "Status", "Rounds", "Completion Notes" # <-- NEW FIELDS
]
PASSWORD = "Mkr@j55905" # It's better to move this to secrets.toml as well

st.set_page_config(layout="wide", page_title="Job Tracker")

# -------------------------
# FIREBASE SETUP
# -------------------------
@st.cache_resource
def init_firebase():
    """Initialize Firebase connection."""
    try:
        firebase_config = st.secrets.get("firebase", {})
        if not firebase_config:
            st.error("Firebase configuration not found in secrets.")
            st.stop()
        
        # Necessary check to prevent re-initialization error
        if not firebase_admin._apps:
            cred = credentials.Certificate(dict(firebase_config))
            firebase_admin.initialize_app(cred)
            
        return firestore.client()
    except Exception as e:
        st.error(f"Firebase initialization failed: {e}")
        st.stop()

# Initialize Firebase and Gemini
db = init_firebase()
COLLECTION_NAME = "job_applications"

API_KEY = st.secrets.get("GEMINI_API_KEY")
if not API_KEY:
    st.error("Please set GEMINI_API_KEY in Streamlit secrets.")
    st.stop()
genai.configure(api_key=API_KEY)


# -------------------------
# DATE UTILITY FUNCTIONS (Largely Unchanged)
# -------------------------
def parse_flexible_date(date_str) -> datetime:
    if not date_str or str(date_str).strip() == "":
        return None
    try:
        # Using fuzzy parsing is more robust for varied inputs
        return parser.parse(str(date_str), fuzzy=True, dayfirst=True)
    except (ValueError, TypeError):
        return None

def normalize_date(value) -> str:
    if not value or str(value).strip() == "":
        return ""
    try:
        dt = parse_flexible_date(value)
        return dt.strftime("%d-%m-%Y") if dt else ""
    except:
        return ""

def display_date(value) -> str:
    return str(value) if value else "Not Specified"

def get_deadline_color(deadline: str) -> str:
    if not deadline or deadline == "Not Specified":
        return "gray"
    try:
        deadline_dt = parse_flexible_date(deadline)
        if not deadline_dt:
            return "gray"
        
        delta = (deadline_dt.date() - datetime.now().date()).days
        if delta < 0: return "red"
        elif delta <= 1: return "orange"
        elif delta <= 3: return "yellow"
        else: return "green"
    except:
        return "gray"

# -------------------------
# FIREBASE OPERATIONS (Updated create_job)
# -------------------------
def create_job(job_data: dict) -> tuple[bool, str]:
    """Create a new job in Firebase with new status fields."""
    try:
        data = {col: job_data.get(col, "") for col in EXPECTED_COLS}
        data["Application Deadline"] = normalize_date(data.get("Application Deadline"))
        data["Date Added"] = datetime.now().strftime("%d-%m-%Y")
        
        # Set initial status and empty fields for new features
        data["Status"] = "Open for Application"
        data["Rounds"] = []
        data["Completion Notes"] = ""
        
        doc_ref = db.collection(COLLECTION_NAME).add(data)
        return True, doc_ref[1].id
    except Exception as e:
        return False, str(e)

def read_jobs() -> pd.DataFrame:
    """Read all jobs from Firebase."""
    try:
        docs = db.collection(COLLECTION_NAME).stream()
        jobs = [doc.to_dict() | {'_id': doc.id} for doc in docs]
        
        if not jobs:
            return pd.DataFrame(columns=EXPECTED_COLS + ['_id'])
            
        df = pd.DataFrame(jobs)
        # Ensure all expected columns exist, filling missing ones with defaults
        for col in EXPECTED_COLS:
            if col not in df.columns:
                df[col] = "" if col not in ["Rounds"] else [[] for _ in range(len(df))]
        
        return df[EXPECTED_COLS + ['_id']]
    except Exception as e:
        st.error(f"Error reading jobs: {e}")
        return pd.DataFrame(columns=EXPECTED_COLS + ['_id'])

def update_job(doc_id: str, updates: dict) -> tuple[bool, str]:
    """Update a job in Firebase."""
    try:
        db.collection(COLLECTION_NAME).document(doc_id).update(updates)
        return True, "Updated successfully"
    except Exception as e:
        return False, str(e)

def delete_job(doc_id: str) -> tuple[bool, str]:
    """Delete a job from Firebase."""
    try:
        db.collection(COLLECTION_NAME).document(doc_id).delete()
        return True, "Deleted successfully"
    except Exception as e:
        return False, str(e)

def check_duplicate(company: str) -> bool:
    """Check if company already exists."""
    try:
        docs = db.collection(COLLECTION_NAME).where("Company Name", "==", company).stream()
        return any(doc.exists for doc in docs)
    except:
        return False

# -------------------------
# AI EXTRACTION (Unchanged)
# -------------------------
def extract_job_details(text: str) -> dict:
    prompt = """
    You are an expert at extracting job posting details from unstructured text. Extract the following fields exactly as JSON:
    - "company_name": The name of the company.
    - "offer_type": Type of offer (e.g., FTE, Intern, PPO, intern + FTE, intern + PPO).
    - "stipend": Stipend amount if mentioned, else "Not Specified".
    - "ctc": CTC amount if mentioned, else "Not Specified".
    - "eligibility": Eligibility criteria (e.g., CGPA, backlogs, branches).
    - "branches": Eligible branches.
    - "role": Job role.
    - "recruitment_process": Description of the recruitment procedure.
    - "application_deadline": Application deadline. Keep the original format as given in text.
    - "form_link": The application form URL.
    - "poc_name": Point of Contact name if mentioned, else "Not Specified".
    - "poc_phone": Point of Contact phone number if mentioned, else "Not Specified".
    
    Return only a valid JSON object. Do not include any markdown formatting.
    
    Text: {text}
    """.format(text=text)
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        # Clean response text from markdown code blocks
        clean_response = re.sub(r'```json\n?|```', '', response.text.strip())
        return json.loads(clean_response)
    except Exception as e:
        st.error(f"Error extracting details: {str(e)}")
        return None

# -------------------------
# PASSWORD AUTHENTICATION
# -------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Authentication Required")
    password_input = st.text_input("Enter Password:", type="password")
    if st.button("Submit"):
        if password_input == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password. Please try again.")
else:
    # -------------------------
    # STREAMLIT UI
    # -------------------------
    st.title("💼 Job Application Tracker")

    # --- Input Section ---
    with st.expander("➕ Add New Job Posting", expanded=False):
        job_text = st.text_area("Paste job posting text here:", height=200)
        if st.button("Parse and Add Job"):
            if job_text:
                with st.spinner("🤖 AI is parsing the details..."):
                    details = extract_job_details(job_text)
                if details:
                    if not check_duplicate(details["company_name"]):
                        new_job = {
                            "Company Name": details.get("company_name", ""),
                            "Offer Type": details.get("offer_type", ""),
                            "Stipend": details.get("stipend", "Not Specified"),
                            "CTC": details.get("ctc", "Not Specified"),
                            "Eligibility": details.get("eligibility", ""),
                            "Branches": details.get("branches", ""),
                            "Role": details.get("role", ""),
                            "Recruitment Process": details.get("recruitment_process", ""),
                            "Application Deadline": details.get("application_deadline", ""),
                            "Form Link": details.get("form_link", ""),
                            "POC Name": details.get("poc_name", "Not Specified"),
                            "POC Phone": details.get("poc_phone", "Not Specified"),
                        }
                        success, result = create_job(new_job)
                        if success:
                            st.success("Job added successfully!")
                            st.rerun()
                        else:
                            st.error(f"Failed to add job: {result}")
                    else:
                        st.warning("Company already exists in tracker!")
                else:
                    st.error("Failed to parse job details. Please check the input text.")
            else:
                st.warning("Please enter job posting text.")

    # --- Display Section ---
    st.subheader("Tracked Companies")
    

    # --- NEW: Filter by Status (Buttons) ---
    status_options = ["All", "Open for Application", "In Process", "Completed"]
    status_filter = st.radio(
        "Filter by:",
        status_options,
        horizontal=True,
        key="status_filter_toggle"
    )
    df = read_jobs()

    if not df.empty:
        # Filter dataframe based on selection
        if status_filter != "All":
            df = df[df["Status"] == status_filter]

        # Always sort by date added (most recent first)
        try:
            df["_sort_date"] = pd.to_datetime(df["Date Added"], errors="coerce", format="%d-%m-%Y")
            df = df.sort_values("_sort_date", ascending=False).drop("_sort_date", axis=1).reset_index(drop=True)
        except Exception:
            pass # Ignore sorting errors if date format is inconsistent

        if df.empty:
            st.info(f"No jobs found with status: '{status_filter}'")

        # Display jobs in sorted order
        for index, row in df.iterrows():
            doc_id = row["_id"]
            deadline = row['Application Deadline']
            deadline_display = display_date(deadline)
            color = get_deadline_color(deadline_display)

            expander_title = f"{row['Company Name']} ({row['Role']}) | Deadline: {deadline_display} | Status: {row.get('Status', 'N/A')}"
            with st.expander(expander_title):
                col1, col2 = st.columns([2, 1])

                with col1: # Job Details
                    st.markdown(f"**Offer Type**: {row['Offer Type']}")
                    st.markdown(f"**CTC**: {row['CTC']} | **Stipend**: {row['Stipend']}")
                    st.markdown(f"**Branches**: {row['Branches']}")
                    st.markdown(f"**Eligibility**: {row['Eligibility']}")
                    st.markdown(f"**Recruitment Process**: {row['Recruitment Process']}")
                    st.markdown(f"**Application Deadline**: <span style='color:{color}; font-weight:bold;'>{deadline_display}</span>", unsafe_allow_html=True)
                    if row['Form Link'] and row['Form Link'] != "Not Specified":
                        st.markdown(f"🔗 [Application Form]({row['Form Link']})")

                with col2: # Status and Actions
                    status_options = ["Open for Application", "In Process", "Completed"]
                    current_status = row.get("Status", "Open for Application")
                    status_index = status_options.index(current_status) if current_status in status_options else 0

                    new_status = st.selectbox(
                        "Update Status",
                        options=status_options,
                        index=status_index,
                        key=f"status_{doc_id}"
                    )

                    if new_status != current_status:
                        update_job(doc_id, {"Status": new_status})
                        st.rerun()

                    if st.button("🗑️ Delete", key=f"delete_{doc_id}"):
                        success, msg = delete_job(doc_id)
                        if success:
                            st.success(f"Deleted {row['Company Name']}!")
                            st.rerun()
                        else:
                            st.error(f"Delete failed: {msg}")

    else:
        st.info("No companies tracked yet. Add a job posting above to get started.")