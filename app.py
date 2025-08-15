import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil import parser
import google.generativeai as genai
import json
import firebase_admin
from firebase_admin import credentials, firestore

# -------------------------
# CONFIG
# -------------------------
EXPECTED_COLS = [
    "Company Name", "Offer Type", "Stipend", "CTC", "Eligibility", "Branches",
    "Role", "Recruitment Process", "Application Deadline", "Form Link",
    "Applied", "Process Completed", "Date Added"
]
PASSWORD = "Mkr@j55905"

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
        
        cred_dict = {
            "type": firebase_config.get("type"),
            "project_id": firebase_config.get("project_id"),
            "private_key_id": firebase_config.get("private_key_id"),
            "private_key": firebase_config.get("private_key").replace("\\n", "\n"),
            "client_email": firebase_config.get("client_email"),
            "client_id": firebase_config.get("client_id"),
            "auth_uri": firebase_config.get("auth_uri"),
            "token_uri": firebase_config.get("token_uri"),
            "auth_provider_x509_cert_url": firebase_config.get("auth_provider_x509_cert_url"),
            "client_x509_cert_url": firebase_config.get("client_x509_cert_url")
        }
        
        if not firebase_admin._apps:
            firebase_admin.initialize_app(credentials.Certificate(cred_dict))
        
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
# ENHANCED DATE UTILITY FUNCTIONS
# -------------------------
def parse_flexible_date(date_str) -> datetime:
    """Parse various date formats including DD.MM.YY, DD/MM/YYYY, etc."""
    if not date_str or str(date_str).strip() == "":
        return None
    
    date_str = str(date_str).strip()
    
    try:
        # Handle DD.MM.YY format (e.g., 12.08.25)
        if "." in date_str and len(date_str.split(".")[-1]) == 2:
            parts = date_str.split(".")
            if len(parts) == 3:
                day, month, year = parts
                full_year = f"20{year}"
                formatted_date = f"{day}/{month}/{full_year}"
                return parser.parse(formatted_date, dayfirst=True)
        
        # Handle DD.MM.YYYY format
        elif "." in date_str:
            date_str = date_str.replace(".", "/")
            return parser.parse(date_str, dayfirst=True)
        
        # Handle standard formats
        else:
            return parser.parse(date_str, dayfirst=True)
            
    except Exception:
        # Fallback: try standard parsing
        try:
            return parser.parse(date_str, dayfirst=True)
        except:
            return None

def normalize_date(value) -> str:
    """Convert date to ISO format (YYYY-MM-DD) for storage."""
    if not value or str(value).strip() == "":
        return ""
    try:
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")
        
        dt = parse_flexible_date(value)
        if dt:
            return dt.strftime("%Y-%m-%d")
        else:
            return ""
    except:
        return ""

def display_date(value) -> str:
    """Format date as DD/MM/YYYY for display."""
    if not value:
        return ""
    try:
        dt = parse_flexible_date(value)
        if dt:
            return dt.strftime("%d/%m/%Y")
        else:
            return str(value)
    except:
        return str(value)

def get_deadline_color(deadline: str) -> str:
    """Get color based on deadline urgency - handles multiple date formats."""
    try:
        if not deadline:
            return "gray"
        
        deadline_dt = parse_flexible_date(deadline)
        if not deadline_dt:
            return "gray"
        
        now = datetime.now()
        delta = (deadline_dt - now).days
        if delta < 0:
            return "red"
        elif delta == 0 or delta == 1:
            return "yellow"
        else:
            return "green"
    except:
        return "gray"

# -------------------------
# FIREBASE OPERATIONS
# -------------------------
def create_job(job_data: dict) -> tuple[bool, str]:
    """Create a new job in Firebase."""
    try:
        data = {col: job_data.get(col, "") for col in EXPECTED_COLS}
        data["Application Deadline"] = normalize_date(data.get("Application Deadline"))
        data["Date Added"] = normalize_date(datetime.now())
        
        for field in ["Applied", "Process Completed"]:
            data[field] = "No"
        
        doc_ref = db.collection(COLLECTION_NAME).add(data)
        return True, doc_ref[1].id
    except Exception as e:
        return False, str(e)

def read_jobs() -> pd.DataFrame:
    """Read all jobs from Firebase."""
    try:
        docs = db.collection(COLLECTION_NAME).stream()
        jobs = []
        for doc in docs:
            job_data = doc.to_dict()
            job_data['_id'] = doc.id
            jobs.append(job_data)
        
        if not jobs:
            return pd.DataFrame(columns=EXPECTED_COLS + ['_id'])
        
        df = pd.DataFrame(jobs)
        for col in EXPECTED_COLS:
            if col not in df.columns:
                df[col] = ""
        
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
# ENHANCED AI EXTRACTION
# -------------------------
def extract_job_details(text: str) -> dict:
    """Extract job details using Gemini AI with enhanced date parsing."""
    prompt = """
    You are an expert at extracting job posting details from unstructured text. Extract the following fields exactly as JSON:
    - "company_name": The name of the company.
    - "offer_type": Type of offer (e.g., FTE, Intern,ppo).
    - "stipend": Stipend amount if mentioned, else "Not Specified".
    - "ctc": CTC amount if mentioned, else "Not Specified".
    - "eligibility": Eligibility criteria (e.g., CGPA, backlogs).
    - "branches": Eligible branches.
    - "role": Job role.
    - "recruitment_process": Description of the recruitment procedure.
    - "application_deadline": Application deadline in DD/MM/YYYY format. If time is mentioned, include it as DD/MM/YYYY HH:MM. If year is not mentioned, assume 2025. Convert any date format to DD/MM/YYYY.
    - "form_link": The application form URL.
    
    IMPORTANT: For dates, always convert to DD/MM/YYYY format. Examples:
    - "10th August" becomes "10/08/2025"
    - "Monday, 11th August, 5PM" becomes "11/08/2025 17:00"
    - "10/08/2025" stays "10/08/2025"
    - "12.08.25" becomes "12/08/2025" (DD.MM.YY format)
    - "25.12.24" becomes "25/12/2024" (DD.MM.YY format)
    - "15.03.26" becomes "15/03/2026" (DD.MM.YY format)
    
    For DD.MM.YY format (like 12.08.25):
    - Treat as DD.MM.YY where YY is 20YY (so 25 = 2025, 24 = 2024, etc.)
    - Convert dots to slashes: 12.08.25 → 12/08/2025
    
    Return only a valid JSON object with these fields. Do not include any markdown formatting, code blocks, or extra text.
    
    Text: {text}
    """.format(text=text)
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        data = json.loads(response_text)
        
        if "application_deadline" in data and data["application_deadline"]:
            deadline = data["application_deadline"]
            if "." in deadline and len(deadline.split(".")[-1]) == 2:
                parts = deadline.split(".")
                if len(parts) == 3:
                    day, month, year = parts
                    full_year = f"20{year}"
                    data["application_deadline"] = f"{day}/{month}/{full_year}"
        
        return data
    except json.JSONDecodeError as e:
        st.error(f"JSON parsing error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error extracting details: {str(e)}")
        return None

# -------------------------
# PASSWORD AUTHORIZATION
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
    # STREAMLIT UI - MATCHES ORIGINAL CSV VERSION
    # -------------------------
    st.title("Job Application Tracker")

    # Input Section
    st.subheader("Add New Job Posting")
    job_text = st.text_area("Paste job posting text here:")

    if st.button("Parse and Add"):
        if job_text:
            details = extract_job_details(job_text)
            if details:
                df = read_jobs()
                if not check_duplicate(details["company_name"]):
                    new_job = {
                        "Company Name": details.get("company_name", "Not Specified"),
                        "Offer Type": details.get("offer_type", "Not Specified"),
                        "Stipend": details.get("stipend", "Not Specified"),
                        "CTC": details.get("ctc", "Not Specified"),
                        "Eligibility": details.get("eligibility", "Not Specified"),
                        "Branches": details.get("branches", "Not Specified"),
                        "Role": details.get("role", "Not Specified"),
                        "Recruitment Process": details.get("recruitment_process", "Not Specified"),
                        "Application Deadline": details.get("application_deadline", "Not Specified"),
                        "Form Link": details.get("form_link", "Not Specified"),
                        "Applied": "No",
                        "Process Completed": "No",
                        "Date Added": datetime.now().strftime("%d/%m/%Y %H:%M")
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

    # Display Section
    st.subheader("Tracked Companies")
    df = read_jobs()

    if not df.empty:
        try:
            df["_sort_date"] = pd.to_datetime(df["Date Added"], errors="coerce")
            df = df.sort_values("_sort_date", ascending=False).drop("_sort_date", axis=1).reset_index(drop=True)
        except:
            pass
        
        for index, row in df.iterrows():
            doc_id = row["_id"]
            deadline = row['Application Deadline']
            deadline_display = display_date(deadline) if deadline else "Not Specified"
            color = get_deadline_color(deadline_display)
            
            headline = f"{row['Company Name']} ({row['Offer Type']}) - Deadline: {deadline_display}"
            
            with st.expander(headline):
                col1, col2, col3 = st.columns([3, 1, 0.5])
                with col1:
                    st.write(f"**Role**: {row['Role']}")
                    st.write(f"**CTC**: {row['CTC']}")
                    st.write(f"**Stipend**: {row['Stipend']}")
                    st.write(f"**Eligibility**: {row['Eligibility']}")
                    st.write(f"**Branches**: {row['Branches']}")
                    st.write(f"**Recruitment Process**: {row['Recruitment Process']}")
                    st.markdown(f"**Application Deadline**: <span style='color:{color}'>{deadline_display}</span>", unsafe_allow_html=True)
                    if row['Form Link'] != "Not Specified" and row['Form Link']:
                        st.markdown(f"[Application Form]({row['Form Link']})")
                with col2:
                    applied_key = f"applied_{doc_id}"
                    completed_key = f"completed_{doc_id}"
                    
                    applied = st.checkbox("Applied", value=row['Applied'] == "Yes", key=applied_key)
                    completed = st.checkbox("Process Completed", value=row['Process Completed'] == "Yes", key=completed_key)
                    
                    current_applied = "Yes" if applied else "No"
                    current_completed = "Yes" if completed else "No"
                    
                    if current_applied != row['Applied']:
                        update_job(doc_id, {"Applied": current_applied})
                    if current_completed != row['Process Completed']:
                        update_job(doc_id, {"Process Completed": current_completed})
                    
                with col3:
                    confirm_key = f"confirm_{doc_id}"
                    if confirm_key not in st.session_state:
                        st.session_state[confirm_key] = False
                    
                    if st.session_state[confirm_key]:
                        st.write("**Confirm Delete?**")
                        col3a, col3b = st.columns(2)
                        with col3a:
                            if st.button("✅ Yes", key=f"yes_{doc_id}", help="Confirm deletion"):
                                st.session_state[confirm_key] = False
                                success, msg = delete_job(doc_id)
                                if success:
                                    st.success(f"Deleted {row['Company Name']} successfully!")
                                    st.rerun()
                                else:
                                    st.error(f"Delete failed: {msg}")
                        with col3b:
                            if st.button("❌ No", key=f"no_{doc_id}", help="Cancel deletion"):
                                st.session_state[confirm_key] = False
                                st.rerun()
                    else:
                        if st.button("🗑️", key=f"delete_{doc_id}", help="Delete this job"):
                            st.session_state[confirm_key] = True
                            st.rerun()
    else:
        st.info("No companies tracked yet. Add a job posting above.")