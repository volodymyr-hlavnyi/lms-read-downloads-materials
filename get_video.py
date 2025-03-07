import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import yt_dlp
import os


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

    # Extract all <a> and <iframe> elements
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

    # Download direct videos
    for video_link in direct_videos:
        filename = video_link.split("/")[-1].split("?")[0]  # Extract file name
        video_path = os.path.join(COURSE_FOLDER, filename)

        print(f"Downloading direct video: {filename}")
        video_resp = requests.get(video_link, stream=True)
        with open(video_path, "wb") as f:
            for chunk in video_resp.iter_content(chunk_size=1024):
                f.write(chunk)

        print(f"Saved: {video_path}")

    # Download Vimeo videos using yt-dlp
    for vimeo_link in vimeo_videos:
        print(f"Downloading Vimeo video: {vimeo_link}")

        ydl_opts = {
            "outtmpl": os.path.join(COURSE_FOLDER, "%(title)s.%(ext)s"),
            "format": "best",
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([vimeo_link])

if __name__ == "__main__":
    load_dotenv()
    username = os.getenv("LMS_USER_NAME")
    password = os.getenv("LMS_PASSWORD")

    # Create a folder to store PDFs
    DOWNLOAD_FOLDER = "pdf_downloads"
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

    COURSE_ID = 135

    download_videos_selenium(COURSE_ID, COURSE_NAME)