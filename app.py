import urllib.parse

import requests
from dotenv import load_dotenv
import os

from requests import session
import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

load_dotenv()
username = os.getenv("LMS_USER_NAME")
password = os.getenv("LMS_PASSWORD")

# Create a folder to store PDFs
DOWNLOAD_FOLDER = "pdf_downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


def login2_to_lms():
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


def get_all_list_my_courses_selenium():
    DASHBOARD_URL = "https://lms.itcareerhub.de/my/"

    # Set up Selenium WebDriver (Headless Mode)
    options = Options()
    options.add_argument("--headless")  # Run without opening a browser
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Initialize WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Log in manually using requests to maintain the session
    session = login2_to_lms()
    cookies = session.cookies.get_dict()

    # Open Moodle dashboard with Selenium
    driver.get(DASHBOARD_URL)

    # Add session cookies from requests to Selenium
    for name, value in cookies.items():
        driver.add_cookie({"name": name, "value": value})

    # Refresh the page after adding cookies
    driver.get(DASHBOARD_URL)

    # Wait for JavaScript to load courses
    driver.implicitly_wait(5)

    # Extract course links
    courses = {}
    course_elements = driver.find_elements(By.XPATH, "//a[contains(@href, 'course/view.php?id=')]")

    for course in course_elements:
        href = course.get_attribute("href")
        course_id = href.split("id=")[-1]
        course_name = course.text.strip()
        if course_name:
            courses[course_id] = course_name

    # Print courses
    print("Available Courses:")
    for course_id, course_name in courses.items():
        print(f"ID: {course_id} - Name: {course_name}")

    # Close Selenium WebDriver
    driver.quit()

    return session, courses


def get_all_pdf_links(session, courses):
    for course_id, course_name in courses.items():
        course_url = f"https://lms.itcareerhub.de/course/view.php?id={course_id}"
        print(f"\nChecking course: {course_name} ({course_id})")

        # Fetch the course page
        resp = session.get(course_url)
        soup = BeautifulSoup(resp.text, "html.parser")

        # Find all PDF links
        pdf_links = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if ".pdf" in href.lower():
                pdf_links.append(href)

        # Print found PDFs
        if pdf_links:
            print("Found PDFs:")
            for pdf in pdf_links:
                print(href)
        else:
            print("No PDFs found in this course.")


def get_all_pdf_links_test(session, courses):
    for course_id, course_name in courses.items():
        course_url = f"https://lms.itcareerhub.de/course/view.php?id={course_id}"
        print(f"\nChecking course: {course_name} ({course_id})")

        # Fetch the course page
        resp = session.get(course_url)
        soup = BeautifulSoup(resp.text, "html.parser")

        # Save the page for inspection
        with open(f"course_{course_id}.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())

        print(f"Saved course_{course_id}.html - Open this file to inspect how PDFs are linked.")
        break  # Stop after the first course for debugging


def get_pdf_links(session, course_id):
    """Extracts all resource links from the course page."""
    course_url = f"https://lms.itcareerhub.de/course/view.php?id={course_id}"
    resp = session.get(course_url)
    soup = BeautifulSoup(resp.text, "html.parser")

    # Find all resource links (PDFs are inside them)
    pdf_page_links = []
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if "mod/resource/view.php?id=" in href:
            pdf_page_links.append(href)

    return pdf_page_links


def prepare_file_name(file_name):
    file_name = urllib.parse.unquote(file_name)
    file_name = file_name.replace(".pptx.pdf", ".pdf")  # Replace .pptx.pdf with .pdf
    file_name = file_name.replace("%20", "_")  # Replace spaces with underscores
    file_name = file_name.replace("%281", "(")  # Replace opening parenthesis
    file_name = file_name.replace("%282", "(")  # Replace opening parenthesis
    file_name = file_name.replace("%283", "[")  # Replace opening square bracket
    file_name = file_name.replace("%29", ")")  # Replace closing parenthesis
    file_name = file_name.replace("%29", "]")  # Replace closing square bracket
    file_name = file_name.replace("()", "")  # Remove empty parentheses
    file_name = file_name.replace("[)", "")  # Remove empty parentheses
    file_name = file_name.replace("_[).", ".")  # Remove empty square brackets
    file_name = file_name.replace("_.", ".")  # Remove empty square brackets
    file_name = file_name.replace(".pptx.", ".")  # Remove .pptx.
    file_name = file_name.replace(".docx.", ".")  # Remove .docx.

    return file_name


def download_pdfs(session, pdf_page_links, name_course_folder=""):
    """Visits each resource page, finds the actual PDF, and downloads it."""

    # Create course-specific folder
    COURSE_FOLDER = os.path.join(DOWNLOAD_FOLDER, name_course_folder)
    os.makedirs(COURSE_FOLDER, exist_ok=True)  # Ensure the folder exists

    for pdf_page in pdf_page_links:
        resp = session.get(pdf_page)
        soup = BeautifulSoup(resp.text, "html.parser")

        # Find the actual PDF download link
        pdf_link = None
        for link in soup.find_all("a", href=True):
            if "pluginfile.php" in link["href"]:
                pdf_link = link["href"]
                break

        if pdf_link:
            # Get filename and download the PDF
            filename = pdf_link.split("/")[-1].split("?")[0]  # Extract file name
            filename = prepare_file_name(filename)
            pdf_path = os.path.join(COURSE_FOLDER, filename)

            print(f"Downloading: {filename} from {pdf_link}")
            pdf_resp = session.get(pdf_link, stream=True)
            with open(pdf_path, "wb") as f:
                for chunk in pdf_resp.iter_content(chunk_size=1024):
                    f.write(chunk)

            print(f"Saved: {pdf_path}")
        else:
            print(f"No PDF found on {pdf_page}")


def get_video_links(session, course_id):
    # Extracts all video resource links from the course page.

    course_url = f"https://lms.itcareerhub.de/course/view.php?id={course_id}"
    resp = session.get(course_url)
    soup = BeautifulSoup(resp.text, "html.parser")

    # Find all resource links (videos may be inside them)
    video_links = []
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if "mod/resource/view.php?id=" in href:
            video_links.append(href)

    return video_links


def download_videos(session, video_page_links, name_course_folder=""):
    """Visits each resource page, finds the actual video, and downloads it."""

    # Create course-specific folder
    COURSE_FOLDER = os.path.join(DOWNLOAD_FOLDER, name_course_folder)
    os.makedirs(COURSE_FOLDER, exist_ok=True)

    for video_page in video_page_links:
        resp = session.get(video_page)
        soup = BeautifulSoup(resp.text, "html.parser")

        # Find the actual video download link
        video_link = None
        for link in soup.find_all("a", href=True):
            if any(ext in link["href"] for ext in [".mp4", ".mov", ".avi", ".mkv", "pluginfile.php"]):
                video_link = link["href"]
                break

        if video_link:
            # Get filename and download the video
            filename = video_link.split("/")[-1].split("?")[0]  # Extract file name
            filename = prepare_file_name(filename)
            video_path = os.path.join(COURSE_FOLDER, filename)

            print(f"Downloading: {filename} from {video_link}")
            video_resp = session.get(video_link, stream=True)
            with open(video_path, "wb") as f:
                for chunk in video_resp.iter_content(chunk_size=1024):
                    f.write(chunk)

            print(f"Saved: {video_path}")
        else:
            print(f"No downloadable video found on {video_page}")


def prepare_name_of_folder_course(course_name):
    return (
        course_name
        .replace("Course name", "")
        .replace(",", "_")
        .replace(" ", "_")
        .replace(".", "_")
        .replace("\n", "")
        .strip()
        .upper()
    )

    # Run the script

def save_course_page(session, course_id):
    """Fetches and saves the HTML of a course page for analysis."""
    course_url = f"https://lms.itcareerhub.de/course/view.php?id={course_id}"
    resp = session.get(course_url)

    # Save the page HTML
    filename = f"course_{course_id}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(resp.text)

    print(f"Saved {filename} - Open this file and check how videos are embedded.")

# Run the function for course 135
if __name__ == "__main__":
    my_session, my_courses = get_all_list_my_courses_selenium()
    save_course_page(my_session, 135)

# if __name__ == "__main__":
#     # Login to LMS and get course list
#     my_session, my_courses = get_all_list_my_courses_selenium()
#
#     # Loop through courses and download PDFs and videos
#     for course_id, course_name in my_courses.items():
#         # PDF files
#         print(f"\nProcessing course: {course_name} ({course_id})")
#         pdf_page_links = get_pdf_links(my_session, course_id)
#         if pdf_page_links:
#             folder_course_name = prepare_name_of_folder_course(course_name)
#             download_pdfs(my_session, pdf_page_links, folder_course_name)
#         else:
#             print("No PDF resources found in this course.")
#         # Video files
#         print(f"\nProcessing course for videos: {course_name} ({course_id})")
#         video_page_links = get_video_links(my_session, course_id)
#         if video_page_links:
#             folder_course_name = prepare_name_of_folder_course(course_name)
#             download_videos(my_session, video_page_links, folder_course_name)
#         else:
#             print("No video resources found in this course.")
