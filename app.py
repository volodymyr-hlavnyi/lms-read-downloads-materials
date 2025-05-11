from base_login import get_all_list_my_courses_selenium
from work_with_pdf.get_pdf import processing_pdf
# from work_with_video.get_video import processing_video

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
                print("Now, it not implemented...")
                # processing_video(my_session, course_id)
