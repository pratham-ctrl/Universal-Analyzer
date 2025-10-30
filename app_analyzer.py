import streamlit as st
import requests
from bs4 import BeautifulSoup
import tempfile
from androguard.core.apk import APK
from fpdf import FPDF
from datetime import datetime
import io
import os

# ---------- Streamlit Setup ----------
st.set_page_config(page_title="Universal App & Website Analyzer", page_icon="🧠", layout="centered")
st.title("🧠 Universal App & Website Analyzer")
st.write("Analyze any APK or Website URL — and generate detailed, well-formatted PDF reports safely.")

option = st.selectbox("Choose what you want to analyze:", ["Website URL", "Upload APK", "APK Download Link"])
result = {}

# ---------- Website Analyzer ----------
def analyze_website(url):
    try:
        page = requests.get(url, timeout=10)
        soup = BeautifulSoup(page.text, "html.parser")
        title = soup.title.string if soup.title else "N/A"
        meta_desc = soup.find("meta", attrs={"name": "description"})
        description = meta_desc["content"] if meta_desc else "N/A"
        links = len(soup.find_all("a"))
        images = len(soup.find_all("img"))
        return {
            "Type": "Website",
            "Title": title,
            "Description": description,
            "Total Links": links,
            "Total Images": images
        }
    except Exception as e:
        return {"Error": f"Website analysis failed: {e}"}

# ---------- Enhanced APK Download with Validation ----------
def download_apk(url):
    """Download APK with proper validation"""
    try:
        # Use headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, timeout=30, headers=headers, stream=True)
        response.raise_for_status()
        
        # Check content type
        content_type = response.headers.get('content-type', '').lower()
        
        # Validate it's not HTML
        if 'text/html' in content_type:
            return None, "The URL points to a webpage, not a direct APK download link. Please provide a direct download URL."
        
        # Read content
        content = response.content
        
        # Validate minimum file size (APKs are typically at least 1MB)
        if len(content) < 100000:  # Less than 100KB is suspicious
            return None, f"Downloaded file is too small ({len(content)} bytes). This might not be a valid APK."
        
        # Validate ZIP/APK signature (first 4 bytes should be 'PK\x03\x04')
        if not content.startswith(b'PK\x03\x04'):
            return None, "Downloaded file is not a valid ZIP/APK format. The file might be corrupted or the link is incorrect."
        
        return content, None
        
    except requests.exceptions.Timeout:
        return None, "Download timeout. The server took too long to respond."
    except requests.exceptions.ConnectionError:
        return None, "Connection error. Please check the URL and your internet connection."
    except requests.exceptions.HTTPError as e:
        return None, f"HTTP error: {e}. The file might not be accessible."
    except Exception as e:
        return None, f"Download failed: {str(e)}"

# ---------- APK Analyzer ----------
def analyze_apk(apk_path):
    try:
        app = APK(apk_path)
        version_name = getattr(app, "get_version_name", lambda: None)() or getattr(app, "get_androidversion_name", lambda: None)()
        version_code = getattr(app, "get_version_code", lambda: None)() or getattr(app, "get_androidversion_code", lambda: None)()
        return {
            "Type": "APK File",
            "App Name": app.get_app_name(),
            "Package Name": app.get_package(),
            "Version Name": version_name,
            "Version Code": version_code,
            "Permissions": app.get_permissions()
        }
    except ValueError as e:
        if "EOCD" in str(e):
            return {"Error": "Invalid APK file: The file is corrupted or not a valid APK/ZIP format. Please ensure you're using a direct download link to an APK file."}
        return {"Error": f"APK parsing error: {e}"}
    except Exception as e:
        return {"Error": f"APK analysis failed: {e}"}

# ---------- Summary Generator ----------
def generate_summary(data):
    if data.get("Type") == "APK File":
        perms = data.get("Permissions", [])
        total = len(perms)
        summary = f"This APK ('{data.get('App Name', 'Unknown')}') requests {total} permissions."
        if total > 30:
            summary += " This app requests many permissions, which could affect user privacy."
        elif total > 10:
            summary += " It requests a moderate number typical for large apps."
        else:
            summary += " It requests few permissions, indicating a lightweight app."
        return summary
    elif data.get("Type") == "Website":
        links = data.get("Total Links", 0)
        images = data.get("Total Images", 0)
        summary = f"The website '{data.get('Title', 'Unnamed')}' contains {links} links and {images} images."
        if links > 100:
            summary += " It appears to be a large, content-heavy website."
        elif links < 20:
            summary += " It seems to be a simple or lightweight site."
        return summary
    return "No summary available."

# ---------- PDF Helper Functions ----------
def clean_text(text):
    """Clean text for PDF output - handle encoding issues"""
    if not isinstance(text, str):
        text = str(text)
    text = text.replace('\u2019', "'").replace('\u2018', "'")
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2013', '-').replace('\u2014', '-')
    cleaned = ''.join(c if ord(c) < 128 else ' ' for c in text)
    return cleaned

def divider(pdf):
    y = pdf.get_y()
    pdf.set_draw_color(200, 200, 200)
    pdf.line(15, y, 195, y)
    pdf.ln(5)

# ---------- Enhanced PDF Class ----------
class PDF(FPDF):
    def header(self):
        self.set_fill_color(41, 128, 185)
        self.rect(0, 0, 210, 25, "F")
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 18)
        self.cell(0, 15, "App & Website Analysis Report", ln=True, align="C")
        self.ln(5)
        self.set_text_color(0, 0, 0)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def section_title(self, title):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(41, 128, 185)
        self.cell(0, 10, title, ln=True)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def add_field(self, label, value):
        self.set_font("Helvetica", "B", 11)
        self.cell(50, 7, clean_text(label) + ":", ln=False)
        self.set_font("Helvetica", "", 11)
        x_start = self.get_x()
        y_start = self.get_y()
        self.multi_cell(0, 7, clean_text(str(value)))
        self.ln(1)

# ---------- Enhanced PDF Generator ----------
def generate_pdf(data):
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", ln=True, align="R")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    
    pdf.section_title("Executive Summary")
    pdf.set_font("Helvetica", "", 11)
    summary = generate_summary(data)
    pdf.multi_cell(0, 7, clean_text(summary))
    pdf.ln(5)
    divider(pdf)
    
    pdf.section_title("General Information")
    
    for key, value in data.items():
        if key not in ["Permissions", "Type"]:
            if value and str(value) not in ["None", "N/A", ""]:
                pdf.add_field(key, value)
    
    pdf.ln(3)
    divider(pdf)
    
    if data.get("Type") == "APK File" and "Permissions" in data:
        permissions = data["Permissions"]
        pdf.section_title(f"Permissions Requested ({len(permissions)} total)")
        pdf.set_font("Helvetica", "", 10)
        
        for i, perm in enumerate(permissions, start=1):
            if pdf.get_y() > 260:
                pdf.add_page()
            
            perm_clean = clean_text(perm)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(10, 6, f"{i}.", ln=False)
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 6, perm_clean)
            pdf.ln(1)
    
    pdf_bytes = pdf.output(dest='S')
    if isinstance(pdf_bytes, str):
        pdf_bytes = pdf_bytes.encode('latin1')
    
    pdf_output = io.BytesIO(pdf_bytes)
    pdf_output.seek(0)
    return pdf_output

# ---------- Main Logic ----------
if option == "Website URL":
    url = st.text_input("Enter Website URL (e.g., https://example.com)")
    if st.button("Analyze Website") and url:
        with st.spinner("Analyzing website..."):
            result = analyze_website(url)
            if "Error" in result:
                st.error(result["Error"])
            else:
                st.success("Analysis complete!")
                st.json(result)

elif option == "Upload APK":
    uploaded_file = st.file_uploader("Upload APK file", type=["apk"])
    if uploaded_file is not None:
        with st.spinner("Analyzing APK..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".apk") as temp_file:
                temp_file.write(uploaded_file.read())
                temp_file_path = temp_file.name
            result = analyze_apk(temp_file_path)
            if "Error" in result:
                st.error(result["Error"])
            else:
                st.success("Analysis complete!")
                st.json(result)
            os.remove(temp_file_path)

elif option == "APK Download Link":
    apk_url = st.text_input("Enter direct APK download link:")
    st.info("💡 Tip: Make sure the URL is a DIRECT download link to an APK file (ends with .apk). Links from app stores or download pages won't work.")
    
    if st.button("Download & Analyze APK") and apk_url:
        with st.spinner("Downloading APK..."):
            content, error = download_apk(apk_url)
            
            if error:
                st.error(f"❌ {error}")
                st.warning("Common issues:\n- URL points to a webpage, not direct APK download\n- File requires authentication/cookies\n- Server blocks automated downloads\n\nTry uploading the APK file manually instead.")
            else:
                temp_path = "downloaded_app.apk"
                try:
                    with open(temp_path, "wb") as f:
                        f.write(content)
                    
                    st.success(f"✅ Downloaded {len(content)} bytes")
                    
                    with st.spinner("Analyzing APK..."):
                        result = analyze_apk(temp_path)
                        
                    if "Error" in result:
                        st.error(result["Error"])
                    else:
                        st.success("Analysis complete!")
                        st.json(result)
                    
                    os.remove(temp_path)
                except Exception as e:
                    st.error(f"File processing error: {e}")

# ---------- PDF Download ----------
if result and "Error" not in result and result != {}:
    pdf_output = generate_pdf(result)
    file_label = result.get("App Name") or result.get("Title") or "analysis_report"
    safe_name = (file_label.replace(" ", "_") if file_label else "analysis_report") + "_report.pdf"
    st.download_button(
        label="📄 Download Detailed Report as PDF",
        data=pdf_output,
        file_name=safe_name,
        mime="application/pdf"
    )
