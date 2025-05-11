from app import processing_video

if __name__ == "__main__":
    # Login to LMS and get course list
    # my_session, my_courses = get_all_list_my_courses_selenium()
    #
    # # Loop through courses and download PDFs and videos
    # for course_id, course_name in my_courses.items():
    #     if course_id == '99':
    #         processing_video(my_session, course_id, course_name)

    processing_video('99', '99')
