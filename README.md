# Project for Downloading Materials from the LMS of IT Hub

## Badges

![License](https://img.shields.io/github/license/volodymyr-hlavnyi/lms-read-downloads-materials)
![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)
![Dependencies](https://img.shields.io/librariesio/github/volodymyr-hlavnyi/lms-read-downloads-materials)

## Attention

This project is provided as an example for demonstrating how to work with authentication and save materials for students who are studying or have studied at IT Hub. 

**Note:** You can only use this project if you have access to the IT Hub LMS.

## Licenses

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

### Third-Party Licenses

The project uses third-party libraries, and their respective licenses are listed in the [THIRD_PARTY_LICENSES.txt](THIRD_PARTY_LICENSES.txt) file.

## Table of Contents

1. [Requirements](#requirements)
2. [Setup .env File](#setup-env-file)
3. [Run the Project](#run-the-project)

## Requirements

- Python 3.6 or higher
- Pipenv or virtual environment
- Google Chrome browser
- ChromeDriver (compatible with your Chrome version)

## Setup .env File

Create a `.env` file in the root directory of the project and add the following content:

```ini
LMS_USER_NAME="your_username"
LMS_PASSWORD="your_password"

DOWNLOAD_FOLDER="LMS_materials_downloads"
```

Replace `your_username` and `your_password` with your actual LMS credentials.

## Run the Project

Before running the project, ensure you have installed all dependencies:

```bash
pip install -r requirements.txt
```

Then, execute the following command to start the script:

```bash
python app.py
```

## Notes

- Ensure that ChromeDriver is correctly installed and its path is set in the system.
- If you face issues with ChromeDriver, check your Chrome version and update it accordingly.
- If running in a virtual environment, activate it before executing the script.

