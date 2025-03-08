import os

from bs4 import BeautifulSoup

from base_login import get_download_folder


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


def download_pdfs(session, pdf_page_links, name_course_folder=""):
    """Visits each resource page, finds the actual PDF, and downloads it."""

    # Create course-specific folder
    DOWNLOAD_FOLDER = get_download_folder()
    COURSE_FOLDER = os.path.join(DOWNLOAD_FOLDER, name_course_folder)
    os.makedirs(COURSE_FOLDER, exist_ok=True)  # Ensure the folder exists

    from work_with_pdf import prepare_file_name

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
