import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

from work_with_pdf import prepare_file_name

# ✅ List of Vimeo URLs
VIMEO_LINKS = [
    "https://player.vimeo.com/video/975302812?h=7778b441db&badge=0&autopause=0&player_id=0&app_id=58479",
    # Add more links here
]

# ✅ Get display environment
DISPLAY = os.getenv("DISPLAY", ":1")  # Ensure this matches your system

# ✅ Set up Firefox options
options = Options()
options.binary_location = "/usr/bin/firefox-esr"  # Adjust if needed
options.add_argument("--start-maximized")

# ✅ Initialize Firefox WebDriver
driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)


def start_screen_recording(output_path, duration=900):
    """Start screen recording using FFmpeg."""
    ffmpeg_cmd = [
        "ffmpeg",
        "-y", "-f", "x11grab",
        "-s", "1280x1024",  # Ensure resolution matches your screen
        "-i", DISPLAY,  # Set correct DISPLAY
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "30",
        output_path
    ]
    return subprocess.Popen(ffmpeg_cmd)


for idx, link in enumerate(VIMEO_LINKS, start=1):
    print(f"🎥 Opening: {link}")

    driver.get(link)
    time.sleep(5)  # Allow page to load

    # ✅ Extract video title
    try:
        title = driver.title or f"video_{idx}"
        print(f"📌 Video Title: {title}")
    except:
        title = f"video_{idx}"

    # ✅ Locate and play the video
    try:
        video_element = driver.find_element("tag name", "video")
        driver.execute_script("arguments[0].play();", video_element)
        print("✅ Video started!")
    except Exception as e:
        print("❌ Could not start video:", e)

    # ✅ Enable Fullscreen
    try:
        driver.execute_script("arguments[0].requestFullscreen();", video_element)
        print("✅ Fullscreen mode enabled!")
    except Exception as e:
        print("⚠️ Fullscreen error:", e)

    # ✅ Get video duration
    try:
        duration = driver.execute_script("return arguments[0].duration;", video_element)
        duration = int(duration) if duration else 900
        print(f"🎥 Video Duration: {duration} seconds")
    except:
        duration = 900
        print("⚠️ Could not retrieve duration, using default 900 seconds")

    # ✅ Start Recording
    video_file = f"{title}.mp4".replace(" ", "_")
    video_file_name = prepare_file_name(video_file)
    recorder = start_screen_recording(video_file_name, duration)

    # ✅ Wait for recording to complete
    try:
        time.sleep(duration + 5)
    finally:
        recorder.terminate()
        print(f"✅ Recording saved: {video_file}")
        driver.quit()

# ✅ Close Browser
driver.quit()
