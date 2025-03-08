from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


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
    from base_login import login2_to_lms, get_credentials

    username, password = get_credentials()
    session = login2_to_lms(username=username, password=password)
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
