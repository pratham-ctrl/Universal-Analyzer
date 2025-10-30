🧠 Universal App & Website Analyzer
🔍 Overview
The Universal App & Website Analyzer is an intelligent Streamlit-based tool that allows users to analyze Android APK files and websites to generate detailed, professional PDF reports.
It provides key technical insights like app permissions, metadata, and website structure in an easy-to-understand format — all in one place.

⚙️ Features
🌐 Website Analyzer
Analyzes any website URL using BeautifulSoup.
Extracts important details such as:
Title and meta description
Total number of links and images
Generates a quick summary based on website size and structure.

📱 APK Analyzer
Extracts information from uploaded APKs using Androguard.
Displays:
App name
Package name
Version code and version name
Permissions requested by the app
Provides a privacy-based summary based on number of permissions.

📄 PDF Report Generator
Automatically generates a clean, structured PDF report.
Includes:
Timestamp of generation
Summary section
General information section
Permissions or website details section
Works without Unicode or rendering errors.
Handles long text safely with auto-splitting and formatting.

🧩 Tech Stack
Frontend: Streamlit
Backend Analysis:
BeautifulSoup4 (for web scraping)
Androguard (for APK analysis)
PDF Generation: fpdf
Others: requests, tempfile, datetime

🚀 How It Works
Choose your analysis type — Website URL, Upload APK, or APK Download Link.
Click Analyze to extract information.
View results instantly in Streamlit.
Download a detailed PDF report with one click.

💡 Use Cases
App and website security review.
Privacy compliance checks.
Quick data extraction for developers and testers.
Research or documentation automation.
