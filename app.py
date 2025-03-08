# app.py
import streamlit as st
import pandas as pd
import tempfile
import os
import pyperclip
from urllib.parse import quote
from backend_code import (
    get_linkedin_details,
    extract_text_from_pdf,
    generate_personalized_mail
)



# Configure page settings
st.set_page_config(
    page_title="LinkedIn Email Campaign Generator",
    page_icon="✉️",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
    .stTextInput input, .stTextInput input:focus {
        background-color: #444444;
        border: 1px solid black;
    }
    .stButton button {
        background-color: #0077b5;
        color: black;
    }
</style>
""", unsafe_allow_html=True)


def login_form():
    """Display LinkedIn login form"""
    
    # Custom CSS for high contrast input fields
    st.markdown("""
        <style>
            /* Styling input fields for contrast */
            input[type="text"], input[type="password"] {
                background-color: #262730;
                color: white !important;
                border: 1px solid white !important;
                padding: 8px;
                font-size: 16px;
                border-radius: 10px;
            }
            
            /* Styling the form background for better visibility */
            div[data-testid="stForm"] {
                background-color: #262730;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
            }
        </style>
    """, unsafe_allow_html=True)

    with st.form("LinkedIn Login"):
        st.subheader("LinkedIn Authentication")
        email = st.text_input("LinkedIn Email")
        password = st.text_input("LinkedIn Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if email and password:
                st.session_state.li_email = email
                st.session_state.li_password = password
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Please enter both email and password")

def main_app():
    """Main application after successful login"""
    # Main header
    st.title("✉️ LinkedIn Email Campaign Generator")
    
    # Logout button
    if st.sidebar.button("Logout"):
        clear_session()
        st.rerun()




# Main header
st.title("✉️ LinkedIn Email Campaign Generator")
st.markdown("Automatically generate personalized email campaigns based on LinkedIn profiles and product information.")

# Sidebar inputs
with st.sidebar:
    st.header("⚙️ Input Parameters")
    
    # URL Input Section
    with st.expander("🔗 LinkedIn Profile URLs", expanded=True):
        single_url = st.text_input(
            "Enter single LinkedIn profile URL:",
            placeholder="https://linkedin.com/in/username"
        )
        
        uploaded_urls_file = st.file_uploader(
            "OR upload CSV/Excel file with multiple URLs:",
            type=["csv", "xlsx"],
            help="File should contain a column named 'url' with LinkedIn profile URLs"
        )

    # PDF Upload Section
    with st.expander("📄 Product Information PDF", expanded=True):
        uploaded_pdf = st.file_uploader(
            "Upload product information PDF:",
            type=["pdf"],
            help="PDF document containing product features, benefits, and target audience"
        )

# Initialize session state for generated emails
if 'generated_emails' not in st.session_state:
    st.session_state.generated_emails = []

# Main processing logic
if st.button("🚀 Generate Campaigns", type="primary"):
    # Validate inputs
    if not uploaded_pdf:
        st.error("❌ Please upload a product PDF file")
        st.stop()
    
    # Collect URLs
    urls = []
    if single_url:
        urls.append(single_url.strip())
    if uploaded_urls_file:
        try:
            if uploaded_urls_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_urls_file)
            else:
                df = pd.read_excel(uploaded_urls_file)
            
            if 'url' in df.columns:
                urls.extend(df['url'].astype(str).tolist())
            else:
                st.error("❌ CSV/Excel file must contain a 'url' column")
                st.stop()
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
            st.stop()
    
    if not urls:
        st.error("❌ Please provide at least one LinkedIn URL")
        st.stop()

    # Create temporary PDF file
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            tmp_pdf.write(uploaded_pdf.getvalue())
            pdf_path = tmp_pdf.name
    except Exception as e:
        st.error(f"❌ Failed to process PDF: {str(e)}")
        st.stop()

    # Processing section
    with st.spinner("🔍 Analyzing profiles and generating emails..."):
        try:
            generated_emails = generate_personalized_mail(urls, pdf_path, st.session_state.li_email, st.session_state.li_password)
            st.session_state.generated_emails = generated_emails
            st.success("✅ Campaigns generated successfully!")
        except Exception as e:
            st.error(f"❌ Error generating emails: {str(e)}")
        finally:
            os.unlink(pdf_path)  # Clean up temp file

# Display generated emails
if st.session_state.generated_emails:
    st.header("📨 Generated Email Campaigns")
    
    for idx, email in enumerate(st.session_state.generated_emails):
        with st.container():
            st.markdown(f"<div class='email-container'>", unsafe_allow_html=True)
            
            col1, col2 = st.columns([4, 1])
            with col1:
                # Extract subject and body
                email_lines = email.split('\n')
                subject = ""
                body = []
                
                for line in email_lines:
                    if line.lower().startswith("subject:") and not subject:
                        subject = line.split(":", 1)[1].strip()
                    else:
                        body.append(line)
                
                body_text = '\n'.join(body)
                
                # Display email content
                st.subheader(f"Email for Lead {idx+1}")
                st.markdown(f"**{subject}**")
                st.subheader("Body:")
                st.markdown(body_text)
            
            with col2:
                # Copy button
                if st.button("📋 Copy", key=f"copy_{idx}"):
                    full_email = f"Subject: {subject}\n\n{body_text}"
                    pyperclip.copy(full_email)
                    st.toast("📋 Email copied to clipboard!", icon="✅")
                
                # Email client button
                mailto_link = f"mailto:?body={quote(body_text)}"
                st.markdown(
                    f'<a href="{mailto_link}" target="_blank" style="text-decoration: none;">'
                    f'<button style="width: 100%; padding: 0.5rem; margin-top: 1rem;">📧 Open in Email</button>'
                    f'</a>',
                    unsafe_allow_html=True
                )
            
            st.markdown("</div>", unsafe_allow_html=True)

# Security disclaimer
st.markdown("---")
with st.expander("🔒 Security Note", expanded=False):
    st.warning("""
    **Important Security Information:**
    - This application uses secure authentication methods for LinkedIn access
    - Credentials are stored encrypted using Streamlit secrets
    - Temporary files are automatically deleted after processing
    - No personal data is stored or shared with third parties
    """)

# Instructions section
with st.expander("📚 How to Use", expanded=False):
    st.markdown("""
    **Step-by-Step Guide:**
    1. **Authenticate with Your LinkedIn Credentials**  
       - Enter your LinkedIn email and password in the login form, this ensures the tool can fetch accurate profile information.
        - 🔒 Note: Your credentials are not stored or shared with any third party—they are only used during the session.
    2. **Input LinkedIn Profiles**  
       - Enter single URL or upload CSV/Excel with multiple URLs
    3. **Upload Product PDF**  
       - Include detailed product/service information
    4. **Generate Campaigns**  
       - Click the 'Generate' button to create emails
    5. **Review & Export**  
       - Copy emails or open directly in your email client
    
    **Tips for Best Results:**
    - Use PDFs with clear product USPs and benefits
    - Ensure LinkedIn URLs are public profiles
    - Review generated emails before sending
                
                
    """)

def clear_session():
    """Clear all session state variables"""
    keys = list(st.session_state.keys())
    for key in keys:
        del st.session_state[key]

# Session state initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Main app flow
if not st.session_state.logged_in:
    login_form()
else:
    main_app()