# Job Application Tracker

A smart web application built with Streamlit that helps students and job seekers track their job applications efficiently. The app uses Google's Gemini AI to automatically extract job details from unstructured text and Firebase for secure cloud data storage, making it easy to organize and monitor your job application pipeline.

## 🚀 Features

- **AI-Powered Job Parsing**: Automatically extract job details from job postings using Google Gemini AI
- **Comprehensive Tracking**: Track company name, offer type, stipend, CTC, eligibility criteria, and more
- **Application Status Management**: Mark applications as applied or process completed
- **Deadline Monitoring**: Visual color-coded deadline tracking (red for overdue, yellow for urgent, green for upcoming)
- **Cloud Data Storage**: Secure Firebase Firestore database for persistent data storage
- **Password Protection**: Secure access with password authentication
- **Enhanced Date Parsing**: Support for multiple date formats including DD.MM.YY, DD/MM/YYYY, and flexible date inputs
- **User-Friendly Interface**: Clean, intuitive Streamlit interface
- **Duplicate Detection**: Prevents adding duplicate companies to the tracker

## 📋 Prerequisites

Before running the application, ensure you have:

- Python 3.7 or higher
- Google Gemini API key
- Firebase project with Firestore database
- Required Python packages (see Installation section)

## 🛠️ Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd application_tracking
   ```

2. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install individually:
   ```bash
   pip install streamlit pandas google-generativeai python-dateutil firebase-admin
   ```

3. **Set up Firebase Project**
   
   a. **Create a Firebase Project**:
   - Go to [Firebase Console](https://console.firebase.google.com)
   - Click "Create a project" or "Add project"
   - Follow the setup wizard
   
   b. **Enable Firestore Database**:
   - In your Firebase project, go to "Firestore Database"
   - Click "Create database"
   - Choose "Start in test mode" (for development)
   - Select a location for your database
   
   c. **Generate Service Account Key**:
   - Go to Project Settings > Service Accounts
   - Click "Generate new private key"
   - Download the JSON file (keep it secure!)

4. **Configure Streamlit Secrets**
   
   Create a `.streamlit/secrets.toml` file in your project directory:
   ```toml
   GEMINI_API_KEY = "your_gemini_api_key_here"
   
   [firebase]
   type = "service_account"
   project_id = "your-project-id"
   private_key_id = "your-private-key-id"
   private_key = "-----BEGIN PRIVATE KEY-----\nyour-private-key\n-----END PRIVATE KEY-----\n"
   client_email = "your-service-account-email@your-project-id.iam.gserviceaccount.com"
   client_id = "your-client-id"
   auth_uri = "https://accounts.google.com/o/oauth2/auth"
   token_uri = "https://oauth2.googleapis.com/token"
   auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
   client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account-email%40your-project-id.iam.gserviceaccount.com"
   ```

5. **Get your Gemini API Key**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Sign in with your Google account
   - Create a new API key
   - Copy the key and add it to your `.streamlit/secrets.toml` file

## 🚀 Usage

1. **Start the application**
   ```bash
   streamlit run app.py
   ```

2. **Authentication**
   - The app will prompt for a password on first access
   - Enter the configured password to access the application
   
3. **Open your browser**
   
   The app will automatically open in your default browser at `http://localhost:8501`

4. **Add job postings**
   - Paste any job posting text in the text area
   - Click "Parse and Add" to automatically extract job details
   - The AI will parse company name, role, CTC, deadlines, and other relevant information
   - Duplicate companies are automatically detected and prevented

5. **Track applications**
   - View all tracked jobs in expandable cards sorted by date added
   - Mark applications as "Applied" or "Process Completed"
   - Monitor deadlines with color-coded indicators
   - Access application forms through provided links
   - Delete job entries with confirmation prompts

## 📊 Data Fields Tracked

The application automatically extracts and tracks the following information:

| Field | Description |
|-------|-------------|
| Company Name | Name of the hiring company |
| Offer Type | Type of position (FTE, Intern, PPO, etc.) |
| Stipend | Monthly stipend for internships |
| CTC | Cost to Company (annual salary) |
| Eligibility | CGPA requirements, branch eligibility |
| Branches | Eligible academic branches |
| Role | Job title/position |
| Recruitment Process | Description of hiring process |
| Application Deadline | Last date to apply |
| Form Link | Application form URL |
| Applied | Status: Whether you've applied |
| Process Completed | Status: Whether recruitment is complete |

## 🎨 Features in Detail

### AI-Powered Parsing
The application uses Google's Gemini AI model to intelligently extract structured data from unstructured job posting text. Simply copy-paste any job announcement, and the AI will identify and categorize all relevant information.

### Enhanced Date Parsing
The application supports multiple date formats:
- **DD/MM/YYYY**: Standard format (e.g., 15/08/2025)
- **DD.MM.YY**: European format (e.g., 15.08.25)
- **Natural language**: "10th August", "Monday, 11th August, 5PM"
- **Flexible parsing**: Automatically converts various formats to standard display

### Smart Deadline Tracking
- 🔴 **Red**: Overdue applications
- 🟡 **Yellow**: Applications due today or tomorrow
- 🟢 **Green**: Upcoming deadlines

### Cloud Data Management
- All data is stored securely in Firebase Firestore
- Real-time synchronization across devices
- Automatic backup and version control
- Scalable and reliable cloud infrastructure

## 🗂️ File Structure

```
application_tracking/
├── app.py                      # Main Streamlit application
├── .streamlit/
│   └── secrets.toml           # Configuration secrets (create this)
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## 🔧 Configuration

### Required Secrets
- `GEMINI_API_KEY`: Your Google Gemini API key (required)
- `firebase`: Complete Firebase service account configuration (required)

### Application Settings
- Password protection is enabled by default (see `PASSWORD` variable in app.py)
- Firebase collection name: "job_applications"
- Supported date formats: DD/MM/YYYY, DD.MM.YY, natural language

### Firebase Configuration
- Data is automatically stored in Firestore database
- Collection: `job_applications`
- Documents contain all job application fields
- Real-time updates and synchronization

## 🌐 Deployment

### Streamlit Cloud Deployment

1. **Push to GitHub**
   - Ensure all files including `requirements.txt` are in your repository
   - Your `.streamlit/secrets.toml` file should NOT be pushed to GitHub for security

2. **Deploy on Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set the main file as `app.py`

3. **Configure Secrets in Streamlit Cloud**
   - In Streamlit Cloud, go to your app settings
   - Add your secrets in the "Secrets" section:
   ```toml
   GEMINI_API_KEY = "your_api_key_here"
   
   [firebase]
   type = "service_account"
   project_id = "your-project-id"
   private_key_id = "your-private-key-id"
   private_key = "-----BEGIN PRIVATE KEY-----\nyour-private-key\n-----END PRIVATE KEY-----\n"
   client_email = "your-service-account-email@your-project-id.iam.gserviceaccount.com"
   client_id = "your-client-id"
   auth_uri = "https://accounts.google.com/o/oauth2/auth"
   token_uri = "https://oauth2.googleapis.com/token"
   auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
   client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account-email%40your-project-id.iam.gserviceaccount.com"
   ```

### Local Development
- Use `.streamlit/secrets.toml` file for local development
- Never commit your secrets file to version control
- Keep your Firebase service account key secure

## 🚨 Troubleshooting

### Common Issues

1. **"Firebase configuration not found in secrets"**
   ```bash
   # Ensure your .streamlit/secrets.toml file exists and contains firebase configuration
   ```

2. **"Please set GEMINI_API_KEY in Streamlit secrets"**
   - Ensure your `.streamlit/secrets.toml` file exists and contains the API key
   - Check that the API key is valid and active

3. **"Firebase initialization failed"**
   - Verify your Firebase service account credentials are correct
   - Ensure Firestore database is enabled in your Firebase project
   - Check that the private key format is correct (with proper line breaks)

4. **"JSON parsing error"**
   - The AI response might be malformed
   - Try rephrasing or simplifying the job posting text
   - Check if the input text contains clear job-related information

5. **Authentication Issues**
   - Check if the password in app.py matches what you're entering
   - Clear browser cache and try again

6. **Date Parsing Issues**
   - The app supports multiple formats: DD/MM/YYYY, DD.MM.YY, natural language
   - If dates aren't parsing correctly, try reformatting the input text

7. **API Rate Limits**
   - Gemini API has usage limits
   - Wait a few minutes before trying again
   - Consider upgrading your API plan for higher limits

## 🤝 Contributing

Contributions are welcome! Here are some ways you can help:

- Report bugs or suggest features
- Improve the AI prompts for better parsing
- Add new tracking fields
- Enhance the user interface
- Add export/import functionality
- Improve Firebase security rules
- Add email notifications for deadlines

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **Streamlit** for the amazing web app framework
- **Google Gemini AI** for intelligent text parsing
- **Firebase** for reliable cloud database services
- **Pandas** for data management capabilities

## 📞 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Review the error messages in the app
3. Ensure all dependencies are properly installed
4. Verify your API key and Firebase configuration are correctly set up
5. Check Firebase console for any service issues

---

**Happy Job Hunting! 🎯**

*Keep track of your applications and never miss a deadline again!*
