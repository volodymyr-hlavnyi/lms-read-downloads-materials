import urllib


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
