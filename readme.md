# Project for Downloading Materials from the LMS of IT Hub

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

If you're using `pipenv`, activate the environment and run:

```bash
pcphange source venv/bin/activateython app.py
```

## Notes

- Ensure that ChromeDriver is correctly installed and its path is set in the system.
- If you face issues with ChromeDriver, check your Chrome version and update it accordingly.
- If running in a virtual environment, activate it before executing the script.

