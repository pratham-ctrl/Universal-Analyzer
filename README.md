# 🧠 Universal App & Website Analyzer

The **Universal App & Website Analyzer** is a Streamlit-based tool that allows you to analyze both **Android APK files** and **Website URLs**.  
It provides detailed insights and automatically generates a **professional PDF report** for every analysis.

---

## 🚀 Features

### 🌐 Website Analyzer
- Extracts **Website Title**, **Meta Description**, **Number of Links**, and **Images**.
- Detects website **technologies** using Wappalyzer.
- Provides an automatic **AI-style summary** describing the website’s structure.
- Handles invalid or unreachable URLs gracefully.

### 📱 APK Analyzer
- Extracts detailed information including:
  - App Name  
  - Package Name  
  - Version Name and Version Code  
  - Permissions Requested
- Generates an **intelligent summary** indicating whether the app is lightweight, moderate, or permission-heavy.
- Works for both **uploaded APK files** and **downloadable APK links**.

### 📄 PDF Report Generator
- Creates **neatly formatted PDF reports** for every analysis.
- Includes:
  - Header with timestamp
  - Auto-generated summary
  - General Information section
  - Permissions or Technologies section
- Professionally styled and compatible across devices.

---

## ⚙️ Tech Stack

| Component | Library / Tool |
|------------|----------------|
| Frontend | Streamlit |
| Web Scraping | BeautifulSoup, Requests |
| APK Analysis | Androguard |
| Report Generation | FPDF |
| File Handling | Tempfile, IO, Datetime |

---

## 🧩 Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/universal-analyzer.git
   cd universal-analyzer
