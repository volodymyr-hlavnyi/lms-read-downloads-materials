import urllib.parse

import requests
from bs4 import BeautifulSoup

from webdriver_manager.chrome import ChromeDriverManager

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

import yt_dlp
import time
import os







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


def download_videos_debug(session, video_page_links, name_course_folder=""):
    """Visits each resource page, finds and downloads videos (direct & Vimeo)."""

    # Create course-specific folder
    COURSE_FOLDER = os.path.join(DOWNLOAD_FOLDER, name_course_folder)
    os.makedirs(COURSE_FOLDER, exist_ok=True)

    for video_page in video_page_links:
        resp = session.get(video_page)
        soup = BeautifulSoup(resp.text, "html.parser")

        video_link = None
        vimeo_links = []

        print(f"\nInspecting {video_page} for video links...")

        # Print all <a> tags to check for video files
        for link in soup.find_all("a", href=True):
            print(f"Found <a> link: {link['href']}")
            if any(ext in link["href"] for ext in [".mp4", ".mov", ".avi", ".mkv", "pluginfile.php"]):
                video_link = link["href"]
                break  # Stop at first direct video

        # Print all <iframe> tags to check for embedded videos
        for iframe in soup.find_all("iframe", src=True):
            print(f"Found <iframe>: {iframe['src']}")
            if "vimeo.com" in iframe["src"]:
                vimeo_links.append(iframe["src"].split("?")[0])  # Clean URL

        # Print extracted video links
        print(f"Direct Video Found: {video_link}" if video_link else "No direct videos found.")
        print(f"Vimeo Videos Found: {vimeo_links}" if vimeo_links else "No Vimeo videos found.")

        # Stop after checking the first resource page for debugging
        break


def download_videos(session, video_page_links, name_course_folder=""):
    """Visits each resource page, finds and downloads videos (direct & Vimeo)."""

    # Create course-specific folder
    COURSE_FOLDER = os.path.join(DOWNLOAD_FOLDER, name_course_folder)
    os.makedirs(COURSE_FOLDER, exist_ok=True)

    for video_page in video_page_links:
        resp = session.get(video_page)
        soup = BeautifulSoup(resp.text, "html.parser")

        video_link = None
        vimeo_links = []

        # Find direct video download links
        for link in soup.find_all("a", href=True):
            if any(ext in link["href"] for ext in [".mp4", ".mov", ".avi", ".mkv", "pluginfile.php"]):
                if link["href"].endswith("pdf") or link["href"].endswith("txt"):
                    continue
                video_link = link["href"]
                break  # Stop at first direct video

        # Find embedded Vimeo videos
        for iframe in soup.find_all("iframe", src=True):
            if "vimeo.com" in iframe["src"]:
                vimeo_links.append(iframe["src"].split("?")[0])  # Clean URL

        # Download direct videos
        if video_link:
            filename = video_link.split("/")[-1].split("?")[0]  # Extract file name
            filename = prepare_file_name(filename)
            video_path = os.path.join(COURSE_FOLDER, filename)

            print(f"Downloading: {filename} from {video_link}")
            video_resp = session.get(video_link, stream=True)
            with open(video_path, "wb") as f:
                for chunk in video_resp.iter_content(chunk_size=1024):
                    f.write(chunk)

            print(f"Saved: {video_path}")

        # Download Vimeo videos using yt-dlp
        for vimeo_link in vimeo_links:
            print(f"Downloading Vimeo video: {vimeo_link}")

            ydl_opts = {
                "outtmpl": os.path.join(COURSE_FOLDER, "%(title)s.%(ext)s"),
                "format": "best",  # Best available quality
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([vimeo_link])

        # If no video found
        if not video_link and not vimeo_links:
            print(f"No downloadable video found on {video_page}")


def download_videos_selenium(course_id, name_course_folder=""):
    """Uses Selenium to find and download videos (direct & Vimeo)."""

    COURSE_FOLDER = os.path.join(DOWNLOAD_FOLDER, name_course_folder)
    os.makedirs(COURSE_FOLDER, exist_ok=True)

    COURSE_URL = f"https://lms.itcareerhub.de/course/view.php?id={course_id}"

    # Set up Selenium WebDriver
    options = Options()
    options.add_argument("--headless")  # Run without opening a browser
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(COURSE_URL)

    # Wait for the page to fully load
    driver.implicitly_wait(5)

    # **1. Scroll down the page to load hidden content**
    scroll_pause_time = 2
    last_height = driver.execute_script("return document.body.scrollHeight")

    for _ in range(5):  # Scroll multiple times
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:  # Stop if no new content loads
            break
        last_height = new_height

    # **2. Try clicking expandable sections**
    try:
        expand_buttons = driver.find_elements(By.CLASS_NAME, "expand-section-class")  # Adjust the class if needed
        for button in expand_buttons:
            driver.execute_script("arguments[0].click();", button)
            time.sleep(2)  # Wait for content to load
    except:
        print("No expandable sections found.")

    # **3. Extract all video-related elements**
    video_links = [a.get_attribute("href") for a in driver.find_elements(By.TAG_NAME, "a") if a.get_attribute("href")]
    iframe_links = [iframe.get_attribute("src") for iframe in driver.find_elements(By.TAG_NAME, "iframe") if
                    iframe.get_attribute("src")]

    driver.quit()

    # Filter direct video links
    direct_videos = [link for link in video_links if
                     any(ext in link for ext in [".mp4", ".mov", ".avi", ".mkv", "pluginfile.php"])]

    # Filter Vimeo videos
    vimeo_videos = [link.split("?")[0] for link in iframe_links if "vimeo.com" in link]

    print(f"\nDirect Video Links: {direct_videos}")
    print(f"Vimeo Videos: {vimeo_videos}")

    # **Download direct videos**
    for video_link in direct_videos:
        filename = video_link.split("/")[-1].split("?")[0]  # Extract file name
        video_path = os.path.join(COURSE_FOLDER, filename)

        print(f"Downloading direct video: {filename}")
        video_resp = requests.get(video_link, stream=True)
        with open(video_path, "wb") as f:
            for chunk in video_resp.iter_content(chunk_size=1024):
                f.write(chunk)

        print(f"Saved: {video_path}")

    # **Download Vimeo videos using yt-dlp**
    for vimeo_link in vimeo_videos:
        print(f"Downloading Vimeo video: {vimeo_link}")

        ydl_opts = {
            "outtmpl": os.path.join(COURSE_FOLDER, "%(title)s.%(ext)s"),
            "format": "best",
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([vimeo_link])


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


if __name__ == "__main__":
    answer = "1"
    while answer != "9":
        print("Select a type: \n1. PDFs \n2. Videos \n3. Both \n9. Exit")
        answer = input("Select a type: ")

        if answer == "9":
            break

        # Login to LMS and get course list
        my_session, my_courses = get_all_list_my_courses_selenium()

        # Loop through courses and download PDFs and videos
        for course_id, course_name in my_courses.items():
            if answer == "1" or answer == "3":
                # PDF files
                print(f"\nProcessing course: {course_name} ({course_id})")
                pdf_page_links = get_pdf_links(my_session, course_id)
                if pdf_page_links:
                    folder_course_name = prepare_name_of_folder_course(course_name)
                    download_pdfs(my_session, pdf_page_links, folder_course_name)
                else:
                    print("No PDF resources found in this course.")

            if answer == "2" or answer == "3":
                # Video files
                print(f"\nProcessing course for videos: {course_name} ({course_id})")
                folder_course_name = prepare_name_of_folder_course(course_name)
                download_videos_selenium(course_id, folder_course_name)
                # video_page_links = get_video_links(my_session, course_id)
                # if video_page_links:
                #     folder_course_name = prepare_name_of_folder_course(course_name)
                #     download_videos(my_session, video_page_links, folder_course_name)
                #
                # else:
                #     print("No video resources found in this course.")
