import streamlit as st
import pandas as pd
import os
from datetime import datetime
from dateutil import parser
import google.generativeai as genai
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
CSV_FILE = "job_tracker.csv"
# Get API key from environment variables
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("Please set the GEMINI_API_KEY in the .env file.")
    st.stop()
genai.configure(api_key=API_KEY)

# Initialize CSV if it doesn't exist
def init_csv():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=[
            "Company Name", "Offer Type", "Stipend", "CTC", "Eligibility",
            "Branches", "Role", "Recruitment Process", "Application Deadline",
            "Form Link", "Applied", "Process Completed", "Date Added"
        ])
        df.to_csv(CSV_FILE, index=False)

# Load CSV data
def load_data():
    init_csv()
    return pd.read_csv(CSV_FILE)

# Save data to CSV
def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# Extract job details using Gemini AI
def extract_job_details(text):
    prompt = """
    You are an expert at extracting job posting details from unstructured text. Extract the following fields exactly as JSON:
    - "company_name": The name of the company.
    - "offer_type": Type of offer (e.g., FTE, Intern, PPO).
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
    
    Return only a valid JSON object with these fields. Do not include any markdown formatting, code blocks, or extra text.
    
    Text: {text}
    """.format(text=text)
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Remove any markdown code block formatting if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Debug: Show the raw response
        st.write("Raw API Response:")
        st.code(response_text)
        
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        st.error(f"JSON parsing error: {str(e)}")
        st.error(f"Raw response: {response.text}")
        return None
    except Exception as e:
        st.error(f"Error extracting details: {str(e)}")
        return None

# Get color for deadline based on current date
def get_deadline_color(deadline):
    try:
        # Handle DD/MM/YYYY format with optional time
        if "/" in deadline:
            # Parse DD/MM/YYYY or DD/MM/YYYY HH:MM format
            deadline_dt = parser.parse(deadline, dayfirst=True)
        else:
            deadline_dt = parser.parse(deadline)
        
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

# Function to delete a job entry
def delete_job(index):
    df = load_data()
    df = df.drop(index).reset_index(drop=True)
    save_data(df)
    st.success("Job deleted successfully!")
    st.rerun()

# Streamlit UI
st.title("Job Application Tracker")

# Input Section
st.subheader("Add New Job Posting")
job_text = st.text_area("Paste job posting text here:")
if st.button("Parse and Add"):
    if job_text:
        details = extract_job_details(job_text)
        if details:
            df = load_data()
            # Check for duplicates
            if details["company_name"] not in df["Company Name"].values:
                new_row = {
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
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df)
                st.success("Job added successfully!")
            else:
                st.warning("Company already exists in tracker!")
        else:
            st.error("Failed to parse job details. Please check the input text.")
    else:
        st.warning("Please enter job posting text.")

# Display Section
st.subheader("Tracked Companies")
df = load_data()

if not df.empty:
    # Add Date Added column if it doesn't exist (for backward compatibility)
    if "Date Added" not in df.columns:
        df["Date Added"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        save_data(df)
    
    # Sort by Date Added (most recent first)
    df = df.sort_values(by="Date Added", ascending=False).reset_index(drop=True)
    
    # Create columns for layout
    for index, row in df.iterrows():
        deadline = row['Application Deadline']
        color = get_deadline_color(deadline)
        
        # Create headline with company name and colored deadline
        headline = f"{row['Company Name']} ({row['Offer Type']}) - Deadline: {deadline}"
        
        with st.expander(headline):
            # Add colored deadline info at the top
            col1, col2, col3 = st.columns([3, 1, 0.5])
            with col1:
                st.write(f"**Role**: {row['Role']}")
                st.write(f"**CTC**: {row['CTC']}")
                st.write(f"**Stipend**: {row['Stipend']}")
                st.write(f"**Eligibility**: {row['Eligibility']}")
                st.write(f"**Branches**: {row['Branches']}")
                st.write(f"**Recruitment Process**: {row['Recruitment Process']}")
                st.markdown(f"**Application Deadline**: <span style='color:{color}'>{deadline}</span>", unsafe_allow_html=True)
                if row['Form Link'] != "Not Specified":
                    st.markdown(f"[Application Form]({row['Form Link']})")
            with col2:
                applied = st.checkbox("Applied", value=row['Applied'] == "Yes", key=f"applied_{index}")
                completed = st.checkbox("Process Completed", value=row['Process Completed'] == "Yes", key=f"completed_{index}")
                # Update CSV when checkboxes change
                df.at[index, "Applied"] = "Yes" if applied else "No"
                df.at[index, "Process Completed"] = "Yes" if completed else "No"
            with col3:
                # Create unique keys for each job's delete state
                delete_key = f"delete_{index}_{row['Company Name'].replace(' ', '_')}"
                confirm_key = f"confirm_{index}_{row['Company Name'].replace(' ', '_')}"
                
                # Initialize confirmation state if not exists
                if confirm_key not in st.session_state:
                    st.session_state[confirm_key] = False
                
                if st.session_state[confirm_key]:
                    # Show confirmation buttons
                    st.write("**Confirm Delete?**")
                    col3a, col3b = st.columns(2)
                    with col3a:
                        if st.button("✅ Yes", key=f"yes_{delete_key}", help="Confirm deletion"):
                            # Reset confirmation state
                            st.session_state[confirm_key] = False
                            # Delete the job
                            df_updated = load_data()
                            df_updated = df_updated.drop(index).reset_index(drop=True)
                            save_data(df_updated)
                            st.success(f"Deleted {row['Company Name']} successfully!")
                            st.rerun()
                    with col3b:
                        if st.button("❌ No", key=f"no_{delete_key}", help="Cancel deletion"):
                            st.session_state[confirm_key] = False
                            st.rerun()
                else:
                    # Show delete button
                    if st.button("🗑️", key=delete_key, help="Delete this job"):
                        st.session_state[confirm_key] = True
                        st.rerun()
                        
            save_data(df)
else:
    st.info("No companies tracked yet. Add a job posting above.")

if __name__ == "__main__":
    st.write("")