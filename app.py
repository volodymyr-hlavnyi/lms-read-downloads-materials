from base_login import get_all_list_my_courses_selenium
from work_with_pdf import get_pdf_links, prepare_name_of_folder_course
from work_with_pdf.get_pdf import download_pdfs
from work_with_video import download_videos_selenium


def processing_pdf(my_session, course_id, course_name):
    print(f"\nProcessing course: {course_name} ({course_id})")
    pdf_page_links = get_pdf_links(my_session, course_id)
    if pdf_page_links:
        folder_course_name = prepare_name_of_folder_course(course_name)
        download_pdfs(my_session, pdf_page_links, folder_course_name)
    else:
        print("No PDF resources found in this course.")


def processing_video(course_id, course_name):
    print(f"\nProcessing course for videos: {course_name} ({course_id})")
    folder_course_name = prepare_name_of_folder_course(course_name)
    download_videos_selenium(course_id, folder_course_name)


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
                processing_pdf(my_session, course_id, course_name)

            if answer == "2" or answer == "3":
                # Video files
                download_videos_selenium(course_id, course_name)
