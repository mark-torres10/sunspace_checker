# Sunspace Yoga Class Checker

This FastAPI application checks the Sunspace yoga website (https://sunspace.ph/collections/yoga) periodically and sends email notifications when classes become available.

## Setup

1. Create and activate the Conda environment:
```bash
conda create -n sunspace_alerts_env python=3.9
conda activate sunspace_alerts_env
```

2. Install required packages:
```bash
pip install requests beautifulsoup4 python-dotenv fastapi uvicorn apscheduler
```

3. Configure the environment variables by creating a `.env` file:
```
CHECK_INTERVAL_MINUTES=1
NOTIFICATION_EMAIL=your_notification_email@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

Note: For Gmail, you'll need to create an App Password. Go to your Google Account settings > Security > 2-Step Verification > App Passwords to generate one.

## Usage

### Running as a FastAPI Application

Start the FastAPI server:
```bash
python app.py
```

The application will:
1. Start a web server on http://localhost:8000
2. Check for available classes every X minutes (configurable via CHECK_INTERVAL_MINUTES)
3. Send email notifications when classes are available

### API Endpoints

- `GET /`: Check service status
- `GET /check-now`: Trigger an immediate class check
- `GET /docs`: API documentation (Swagger UI)

### Email Notifications

When classes become available, you'll receive an email with:
- Subject: "Available classes at Sunspace"
- List of available classes in the format:
```
[Day, Month Date] Class Name, Price
```

Example:
```
[Tuesday, Feb 18] Yoga Basics, P500
[Wednesday, Feb 19] Vinyasa Flow, P500
```

## Features

- FastAPI web server with API endpoints
- Configurable check interval
- Automatic email notifications
- Filters out sold-out classes
- Formats dates and prices consistently
- Includes logging for debugging
- Polite scraping with delays between requests

## Notes

- The script uses the current year for dates since the website doesn't specify the year
- A small delay is added between page requests to be respectful to the server
- Includes error handling for network issues and parsing problems
- Emails are sent via SMTP (supports Gmail with App Passwords) 