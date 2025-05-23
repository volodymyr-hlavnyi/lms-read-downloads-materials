import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

def get_credentials():
    username = os.getenv("LMS_USER_NAME")
    password = os.getenv("LMS_PASSWORD")

    return username, password


def get_download_folder():
    # Create a folder to store PDFs
    DOWNLOAD_FOLDER = os.getenv("DOWNLOAD_FOLDER")
    if not DOWNLOAD_FOLDER:
        #set by default
        DOWNLOAD_FOLDER = "LMS_materials_downloads"
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    return DOWNLOAD_FOLDER


def login2_to_lms(username, password):
    # Define URLs
    LOGIN_PAGE = "https://lms.itcareerhub.de/login/index.php"
    LOGIN_POST = "https://lms.itcareerhub.de/login/index.php"

    # Start a session
    session = requests.Session()

    # Get login page to fetch CSRF token
    resp = session.get(LOGIN_PAGE)
    soup = BeautifulSoup(resp.text, 'html.parser')

    # Extract the token
    token_input = soup.find("input", {"name": "logintoken"})
    if token_input:
        logintoken = token_input["value"]
    else:
        print("Failed to get login token")
        exit()

    # Define login payload
    payload = {
        "username": username,
        "password": password,
        "logintoken": logintoken
    }

    # Perform login
    response = session.post(LOGIN_POST, data=payload)

    # Check if login was successful
    if "Logout" in response.text or "Abmelden" in response.text:
        print("Login successful!")
        return session
    else:
        print("Login failed!")
        return None
