from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import pypdf
# from google import genai 
import streamlit as st
import os
import google.generativeai as genai
from selenium.webdriver.chrome.options import Options



def get_linkedin_details(urls, username, password):
    # chrome_options = Options()
    # # chrome_options.add_argument("--headless=new")  # Required for servers
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--disable-dev-shm-usage")

    # # Dynamically find Chrome path (for Streamlit's environment)
    # try:
    #     chrome_path = subprocess.check_output(["which", "google-chrome"]).decode().strip()
    #     chrome_options.binary_location = chrome_path
    # except:
    #     st.error("Chrome not found! Check setup.sh")
    #     return
    

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")  # Required for cloud environments
    chrome_options.add_argument("--disable-dev-shm-usage")  # Prevent crashes in Docker
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.google.com")

    # Initialize driver
    # driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Login process using provided credentials
        driver.get("https://www.linkedin.com/login")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "username")))
        
        email_field = driver.find_element(By.ID, "username")
        email_field.send_keys(username)
        
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(password)
        
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(3)

        # Check for security checkpoint
        try:
            # Wait up to 10 seconds for security check to appear
            WebDriverWait(driver, 5).until(
                lambda d: 'checkpoint' in d.current_url.lower() or 
                d.find_elements(By.XPATH, "//*[contains(text(), 'Security Verification')]")
            )
            print("Security verification required. Please complete the check in the browser.")
            input("Press Enter here when you've completed the security check...")
            time.sleep(2)  # Additional wait after manual intervention
        except TimeoutException:
            pass  # No security check detected

    except Exception as e:
        print(f"Login failed: {str(e)}")
        driver.quit()
        return None
    

    persons = []
    
    for url in urls:
        driver.get(url)
        time.sleep(4)


        details = {
            'name' : None, 
            'bio' : None,
            'skills': [],
            'activity': {'action' : [], 'content' : []},
            'mutual' : []

        }
        xpath_name = "//h1[contains(@class, 't-24')]"
        xpath_bio = '//*[@id="profile-content"]/div/div[2]/div/div/main/section[1]/div[2]/div[2]/div[1]/div[2]'
        xpath_skills = "//section[.//*[@id='skills']]//div[contains(@class, 'hoverable-link-text')]/span[1]"
        xpath_activity_action = "//section[.//*[@id='content_collections']]//div[contains(@class,'pt1 ph4 t-12 t-black--light')]"
        xpath_activity_content = "//section[.//*[@id='content_collections']]//div[contains(@class,'display-flex flex-row')]"
        xpath_mutual1 = "//a[contains(@class, 'inline-flex align-items-center link-without-hover-visited pt2')]"
        xpath_mutual2 = "//ul[contains(@role, 'list')]//div[contains(@data-view-name, 'search-entity-result-universal-template')]//div[2]//div[1]//span[contains(@aria-hidden, 'true')]"

        
        try:

            # Name
            details['name'] = driver.find_element(By.XPATH, xpath_name).text

            # Bio
            details['bio'] = driver.find_element(By.XPATH, xpath_bio).text

            
            # Skills
            skills = driver.find_elements(By.XPATH, xpath_skills)
            details['skills'] = [skill.text for skill in skills]
            
            # Activity (requires expanding posts)
            details['activity']['action'] = [x.text for x in driver.find_elements(By.XPATH, xpath_activity_action)]
            details['activity']['content'] = [x.text for x in driver.find_elements(By.XPATH, xpath_activity_content)]


            # Wait until the element is clickable and then click
            time.sleep(2)
            driver.find_element(By.XPATH, xpath_mutual1).click()
            time.sleep(5)


            # Get mutual connections
            details['mutual'] = [a.text for a in driver.find_elements(By.XPATH, xpath_mutual2)]

            persons.append(details)
            

            
        except Exception as e:
            print(f"Exception: {str(e)}")
            continue

        
    
    driver.quit()
    return persons






### READING TEXT FROM PDF AND GET INFO ABOUT PRODUCT

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, "rb") as file:
        reader = pypdf.PdfReader(file)
        text = "".join(page.extract_text() or "" for page in reader.pages)
    return text

# def query_llm_api(prompt: str):
#     client = genai.Client(api_key="AIzaSyCm-tgMWstlFOrmkHYTXurua0g1jPmuYaA")

#     response = client.models.generate_content(
#         model="gemini-2.0-flash",
#         contents=prompt
#     )

#     return response.text


def query_llm_api(prompt: str) -> str:
    """
    Get response from Gemini API using the provided prompt
    WARNING: Hardcoded API keys are insecure - only use for testing
    """
    try:
        # SECURITY NOTE: This exposes your API key in the code
        api_key = "AIzaSyCm-tgMWstlFOrmkHYTXurua0g1jPmuYaA"  # ⚠️ Your live key here
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        return response.text
    
    except Exception as e:
        return f"Error generating response: {str(e)}"

# def query_llm_api(prompt: str) -> str:
#     """
#     Get response from Gemini API using the provided prompt
    
#     Args:
#         prompt: User input prompt
    
#     Returns:
#         Generated response as string
#     """
#     try:
#         # Get API key from environment variable (never hardcode in production)
#         api_key = os.getenv("AIzaSyCm-tgMWstlFOrmkHYTXurua0g1jPmuYaA")
        
#         if not api_key:
#             raise ValueError("GOOGLE_API_KEY environment variable not set")
        
#         # Configure the API key properly
#         genai.configure(api_key=api_key)
        
#         # Create model instance with specified model
#         model = genai.GenerativeModel('gemini-2.0-flash')
        
#         # Generate response
#         response = model.generate_content(prompt)
        
#         return response.text
    
#     except Exception as e:
#         return f"Error generating response: {str(e)}"


### GENERATING PERSONALISE EMAIL




def generate_personalized_mail(profile_urls, pdf_path, username, password):
    response = []
    """Modified to accept credentials"""
    extracted_text = extract_text_from_pdf(pdf_path)
    lead_details = get_linkedin_details(profile_urls, username, password)
    instructed_prompt = "Based on the above text, write 3 personalized emails to the lead (whose details are provided) in a concise manner, keeping in mind they have limited time to read the email. Each email should have:  1. **Subject:** The subject line should be catchy, highly personalized and relevant to the lead’s profile. 2. **Body:** The email body should be structured naturally, incorporating:  - A personalized introduction  - Key product features, unique selling points (USPs), and benefits tailored to the lead’s profile, without explicitly labeling them as separate sections.  - A persuasive closing with a compelling call to action (CTA) to encourage engagement (e.g., scheduling a demo, signing up for a trial, etc.).  Ensure that all elements (introduction, product benefits, CTA) are woven into the body fluidly without explicit section headers like 'Introduction' or 'Call to Action.'  Also, just provide the email content as requested. Do not include any introductory or concluding remarks like 'Here's your template' or 'Let me know if you need anything else.' The response should contain **only the emails** in the specified format. At the end of mail, Greet with regards, your name and contact details (take from product pdf, if provided, else leave as template) "

    for lead in lead_details:
        email_template = query_llm_api(f"Details about the product:\n{extracted_text}\n"
                               f"Information about lead:\n{lead}\n"
                               f"Prompt:\n{instructed_prompt}")
        response.append(email_template)
    
    return response




# if __name__ == "__main__":
#     pdf_path = "product_info.pdf"
#     profile_urls = ["https://www.linkedin.com/in/anuragrathore/", "https://www.linkedin.com/in/anshulvikrampandey/"]

#     generated_mails =  generate_personalized_mail(profile_urls, pdf_path)
#     print(generated_mails[1])