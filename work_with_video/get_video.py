import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from base_login import get_download_folder, get_credentials, login2_to_lms
from work_with_pdf import prepare_name_of_folder_course, prepare_file_name
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager

from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager


def processing_video(course_id, course_name):
    print(f"\nProcessing course for videos: {course_name} ({course_id})")
    folder_course_name = prepare_name_of_folder_course(course_name)
    download_videos_selenium(course_id, folder_course_name)


def start_screen_recording(output_path, duration):
    """Start screen recording using FFmpeg."""
    ffmpeg_cmd = [
        "ffmpeg", "-y", "-f", "x11grab", "-s", "1280x1024", "-i", ":1",
        "-t", str(duration), "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23", output_path
    ]
    return subprocess.Popen(ffmpeg_cmd)


def download_videos_selenium(course_id, name_course_folder=""):
    """Finds and plays videos, records screen, and saves output."""
    DOWNLOAD_FOLDER = get_download_folder()
    COURSE_FOLDER = os.path.join(DOWNLOAD_FOLDER, name_course_folder)
    os.makedirs(COURSE_FOLDER, exist_ok=True)

    COURSE_URL = f"https://lms.itcareerhub.de/course/view.php?id={course_id}"
    # options = Options()
    # options.add_argument("--start-maximized")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    # Set up Firefox WebDriver
    options = Options()
    options.binary_location = "/usr/bin/firefox-esr"  # Update this if your path is different

    # Initialize driver
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)

    username, password = get_credentials()
    session = login2_to_lms(username=username, password=password)
    cookies = session.cookies.get_dict()

    driver.get(COURSE_URL)

    # Add session cookies from requests to Selenium
    for name, value in cookies.items():
        driver.add_cookie({"name": name, "value": value})

    driver.get(COURSE_URL)  # Reload after setting cookies

    sections = driver.find_elements(By.XPATH, "//*")  # Get ALL elements
    print(f"Total elements on page: {len(sections)}")
    # for section in sections:
    #     print(section.get_attribute("outerHTML"))

    wait = WebDriverWait(driver, 5)  # Wait up to 10 seconds
    sections = driver.find_elements(By.XPATH, "//li[contains(@id, 'section-')]")

    for section in sections:
        try:
            title_element = section.find_element(By.CLASS_NAME, "sectionname")
            session_name = title_element.text.strip()
            session_name = prepare_file_name(session_name)
            print(f"📌 Processing: {session_name}")
        except:
            continue

        try:
            play_button = section.find_element(By.CSS_SELECTOR, "a[aria-label^='Занятие']")
            play_button.click()
            time.sleep(3)
        except:
            print("⚠️ Play button not found, trying JavaScript...")
            driver.execute_script("document.querySelector('video').play();")

        try:
            video_element = driver.find_element(By.TAG_NAME, "video")
            driver.execute_script("""
                let video = arguments[0];
                video.muted = true;  // Required for autoplay on some browsers
                video.play();
            """, video_element)

            # ✅ Retry 10 times to ensure playback starts
            for attempt in range(10):
                is_playing = driver.execute_script("return !arguments[0].paused;", video_element)
                if is_playing:
                    print(f"✅ Video is playing after {attempt + 1} attempts!")
                    break  # Exit loop if video starts playing
                print(f"⏳ Video still not playing... retrying {attempt + 1}/10")

                # Force reattempt
                driver.execute_script("arguments[0].play();", video_element)
                time.sleep(2)

            else:
                print("❌ Video failed to play after multiple attempts!")

        except Exception as e:
            print("❌ Error finding video element:", e)

        # ✅ Check if video is playing
        time.sleep(3)
        is_playing = driver.execute_script("return !arguments[0].paused;", video_element)
        if is_playing:
            print("✅ Video is playing!")
        else:
            print("❌ Video is still not playing!")

        # ✅ Try to get video duration
        video_duration = None
        retries = 0
        while video_duration is None and retries < 10:
            time.sleep(2)
            video_duration = driver.execute_script("return arguments[0].duration || null;", video_element)
            retries += 1

        if video_duration:
            print(f"🎥 Video Duration: {video_duration} seconds")
        else:
            print("⚠️ Could not retrieve video duration, using fallback time!")
            video_duration = 900  # 15 minutes fallback

        # ✅ Start recording
        ffmpeg_process = start_screen_recording(video_file, duration=int(video_duration))

        # ✅ Monitor video playback
        while driver.execute_script("return !arguments[0].ended;", video_element):
            print("⏳ Video is still playing...")
            time.sleep(5)

        # ✅ Stop recording
        ffmpeg_process.terminate()
        print(f"✅ Recording saved: {video_file}")

        driver.quit()

# def start_screen_recording(output_path, duration=900):
#     """Start screen recording using FFmpeg with Xvfb (Virtual Display)."""
#     ffmpeg_cmd = [
#         "xvfb-run", "-a",  # Run in a virtual X server
#         "ffmpeg",
#         "-y",  # Overwrite existing file
#         "-f", "x11grab",
#         "-s", "1280x1024",  # Adjust to your screen resolution
#         "-i", ":99.0",  # Use Xvfb virtual display
#         "-t", str(duration),
#         "-c:v", "libx264",
#         "-preset", "ultrafast",
#         "-crf", "23",
#         output_path
#     ]
#
#     return subprocess.Popen(ffmpeg_cmd)
#
#
# def processing_video(my_session, course_id, course_name):
#     print(f"\nProcessing course for videos: {course_name} ({course_id})")
#     folder_course_name = prepare_name_of_folder_course(course_name)
#     download_videos_selenium(my_session, course_id, folder_course_name)
#
#
# def download_videos_selenium(session, course_id, name_course_folder=""):
#     """Uses Selenium to open a video and record it."""
#
#     DOWNLOAD_FOLDER = get_download_folder()
#     COURSE_FOLDER = os.path.join(DOWNLOAD_FOLDER, name_course_folder)
#     os.makedirs(COURSE_FOLDER, exist_ok=True)
#
#     COURSE_URL = f"https://lms.itcareerhub.de/course/view.php?id={course_id}"
#     video_file = os.path.join(COURSE_FOLDER, f"{course_id}_recorded.mp4")
#
#     # ✅ Set up Selenium WebDriver
#     options = Options()
#     options.add_argument("--start-maximized")  # Ensure full screen
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#
#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
#
#     username, password = get_credentials()
#     session = login2_to_lms(username=username, password=password)
#     cookies = session.cookies.get_dict()
#
#     driver.get(COURSE_URL)
#
#     # Add session cookies from requests to Selenium
#     for name, value in cookies.items():
#         driver.add_cookie({"name": name, "value": value})
#
#     driver.get(COURSE_URL)  # Reload after setting cookies
#
#     WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
#
#     print(f"Recording screen for course {course_id}...")
#
#     # ✅ Switch to iframe if present
#     try:
#         iframe = driver.find_element(By.TAG_NAME, "iframe")
#         driver.switch_to.frame(iframe)
#         print("✅ Switched to iframe!")
#     except:
#         print("❌ No iframe found!")
#
#     # ✅ Locate the video player
#     try:
#         video_element = driver.find_element(By.TAG_NAME, "video")
#     except:
#         print("❌ No video element found!")
#         driver.quit()
#         return
#
#     # ✅ Try clicking the Play button
#     # try:
#     #     play_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "PlayButton_module_playButtonWrapper")))
#     #     play_button.click()
#     #     print("✅ Play button clicked!")
#     # except:
#     #     print("❌ Could not find Play button, trying JavaScript...")
#     #     driver.execute_script("arguments[0].play();", video_element)
#
#     # ✅ Try to play video using JavaScript with retries
#     try:
#         video_element = driver.find_element(By.TAG_NAME, "video")
#         driver.execute_script("""
#             let video = arguments[0];
#             video.muted = true;  // Required for autoplay on some browsers
#             video.play();
#         """, video_element)
#
#         # ✅ Retry 10 times to ensure playback starts
#         for attempt in range(10):
#             is_playing = driver.execute_script("return !arguments[0].paused;", video_element)
#             if is_playing:
#                 print(f"✅ Video is playing after {attempt + 1} attempts!")
#                 break  # Exit loop if video starts playing
#             print(f"⏳ Video still not playing... retrying {attempt + 1}/10")
#
#             # Force reattempt
#             driver.execute_script("arguments[0].play();", video_element)
#             time.sleep(2)
#
#         else:
#             print("❌ Video failed to play after multiple attempts!")
#
#     except Exception as e:
#         print("❌ Error finding video element:", e)
#
#     # ✅ Check if video is playing
#     time.sleep(3)
#     is_playing = driver.execute_script("return !arguments[0].paused;", video_element)
#     if is_playing:
#         print("✅ Video is playing!")
#     else:
#         print("❌ Video is still not playing!")
#
#     # ✅ Try to get video duration
#     video_duration = None
#     retries = 0
#     while video_duration is None and retries < 10:
#         time.sleep(2)
#         video_duration = driver.execute_script("return arguments[0].duration || null;", video_element)
#         retries += 1
#
#     if video_duration:
#         print(f"🎥 Video Duration: {video_duration} seconds")
#     else:
#         print("⚠️ Could not retrieve video duration, using fallback time!")
#         video_duration = 900  # 15 minutes fallback
#
#     # ✅ Start recording
#     ffmpeg_process = start_screen_recording(video_file, duration=int(video_duration))
#
#     # ✅ Monitor video playback
#     while driver.execute_script("return !arguments[0].ended;", video_element):
#         print("⏳ Video is still playing...")
#         time.sleep(5)
#
#     # ✅ Stop recording
#     ffmpeg_process.terminate()
#     print(f"✅ Recording saved: {video_file}")
#
#     driver.quit()
