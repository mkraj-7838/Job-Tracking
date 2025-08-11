# Job Application Tracker

A smart web application built with Streamlit that helps students and job seekers track their job applications efficiently. The app uses Google's Gemini AI to automatically extract job details from unstructured text, making it easy to organize and monitor your job application pipeline.

## 🚀 Features

- **AI-Powered Job Parsing**: Automatically extract job details from job postings using Google Gemini AI
- **Comprehensive Tracking**: Track company name, offer type, stipend, CTC, eligibility criteria, and more
- **Application Status Management**: Mark applications as applied or process completed
- **Deadline Monitoring**: Visual color-coded deadline tracking (red for overdue, yellow for urgent, green for upcoming)
- **Data Persistence**: All data is stored in CSV format for easy access and backup
- **User-Friendly Interface**: Clean, intuitive Streamlit interface

## 📋 Prerequisites

Before running the application, ensure you have:

- Python 3.7 or higher
- Google Gemini API key
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
   pip install streamlit pandas python-dotenv google-generativeai python-dateutil
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. **Get your Gemini API Key**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Sign in with your Google account
   - Create a new API key
   - Copy the key and add it to your `.env` file

## 🚀 Usage

1. **Start the application**
   ```bash
   streamlit run app.py
   ```

2. **Open your browser**
   
   The app will automatically open in your default browser at `http://localhost:8501`

3. **Add job postings**
   - Paste any job posting text in the text area
   - Click "Parse and Add" to automatically extract job details
   - The AI will parse company name, role, CTC, deadlines, and other relevant information

4. **Track applications**
   - View all tracked jobs in expandable cards
   - Mark applications as "Applied" or "Process Completed"
   - Monitor deadlines with color-coded indicators
   - Access application forms through provided links

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

### Smart Deadline Tracking
- 🔴 **Red**: Overdue applications
- 🟡 **Yellow**: Applications due today or tomorrow
- 🟢 **Green**: Upcoming deadlines

### Data Management
- All data is stored in `job_tracker.csv`
- Easy to backup, share, or import into other tools
- Persistent storage across app sessions

## 🗂️ File Structure

```
application_tracking/
├── app.py                 # Main Streamlit application
├── job_tracker.csv        # Data storage file (auto-generated)
├── .env                   # Environment variables (create this)
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🔧 Configuration

### Environment Variables
- `GEMINI_API_KEY`: Your Google Gemini API key (required)

### CSV Storage
- Data is automatically saved to `job_tracker.csv`
- File is created automatically on first run
- Can be opened in Excel or Google Sheets for additional analysis

## 🌐 Deployment

### Streamlit Cloud Deployment

1. **Push to GitHub**
   - Ensure all files including `requirements.txt` are in your repository
   - Your `.env` file should NOT be pushed to GitHub for security

2. **Deploy on Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set the main file as `app.py`

3. **Configure Secrets**
   - In Streamlit Cloud, go to your app settings
   - Add your secrets in the "Secrets" section:
   ```toml
   GEMINI_API_KEY = "your_api_key_here"
   ```

### Local Development
- Use `.env` file for local development
- Never commit your `.env` file to version control

## 🚨 Troubleshooting

### Common Issues

1. **"No module named 'dotenv'"**
   ```bash
   pip install python-dotenv
   ```

2. **"Please set the GEMINI_API_KEY"**
   - Ensure your `.env` file exists and contains the API key
   - Check that the API key is valid and active

3. **"JSON parsing error"**
   - The AI response might be malformed
   - Check the "Raw API Response" debug output
   - Try rephrasing or simplifying the job posting text

4. **API Rate Limits**
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

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **Streamlit** for the amazing web app framework
- **Google Gemini AI** for intelligent text parsing
- **Pandas** for data management capabilities

## 📞 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Review the error messages in the app
3. Ensure all dependencies are properly installed
4. Verify your API key is correctly configured

---

**Happy Job Hunting! 🎯**

*Keep track of your applications and never miss a deadline again!*
