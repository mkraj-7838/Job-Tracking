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
            "Form Link", "Applied", "Process Completed"
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
    - "application_deadline": Application deadline date and time (in ISO format YYYY-MM-DDTHH:MM, assume current year if not specified).
    - "form_link": The application form URL.
    
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
                    "Process Completed": "No"
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
    # Create columns for layout
    for index, row in df.iterrows():
        with st.expander(f"{row['Company Name']} ({row['Offer Type']})"):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**Role**: {row['Role']}")
                st.write(f"**CTC**: {row['CTC']}")
                st.write(f"**Stipend**: {row['Stipend']}")
                st.write(f"**Eligibility**: {row['Eligibility']}")
                st.write(f"**Branches**: {row['Branches']}")
                st.write(f"**Recruitment Process**: {row['Recruitment Process']}")
                deadline = row['Application Deadline']
                color = get_deadline_color(deadline)
                st.markdown(f"**Application Deadline**: <span style='color:{color}'>{deadline}</span>", unsafe_allow_html=True)
                if row['Form Link'] != "Not Specified":
                    st.markdown(f"[Application Form]({row['Form Link']})")
            with col2:
                applied = st.checkbox("Applied", value=row['Applied'] == "Yes", key=f"applied_{index}")
                completed = st.checkbox("Process Completed", value=row['Process Completed'] == "Yes", key=f"completed_{index}")
                # Update CSV when checkboxes change
                df.at[index, "Applied"] = "Yes" if applied else "No"
                df.at[index, "Process Completed"] = "Yes" if completed else "No"
            save_data(df)
else:
    st.info("No companies tracked yet. Add a job posting above.")

if __name__ == "__main__":
    st.write("Set GEMINI_API_KEY in environment variables to use the app.")