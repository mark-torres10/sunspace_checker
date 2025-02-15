import os
from fastapi import FastAPI, HTTPException
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from revised_sunspace_checker import RevisedSunspaceChecker
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = FastAPI(title="Sunspace Class Checker")

# Initialize the checker
checker = RevisedSunspaceChecker()

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL")
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "1"))

def send_email(available_classes):
    """Send email notification with available classes"""
    if not all([SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, NOTIFICATION_EMAIL]):
        logging.error("Email configuration is incomplete")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = NOTIFICATION_EMAIL
        msg['Subject'] = "Available classes at Sunspace"

        body = "The following classes are currently available:\n\n"
        body += "\n".join(available_classes)
        body += "\n\nBook now at: https://sunspace.ph/collections/yoga"

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
            
        logging.info(f"Email notification sent to {NOTIFICATION_EMAIL}")
    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")

def check_classes():
    """Check for available classes and send notification if found"""
    try:
        available_classes = checker.check_all_pages()
        if available_classes:
            logging.info(f"Found {len(available_classes)} available classes")
            send_email(available_classes)
        else:
            logging.info("No available classes found")
    except Exception as e:
        logging.error(f"Error checking classes: {str(e)}")

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(
    check_classes,
    trigger=IntervalTrigger(minutes=CHECK_INTERVAL_MINUTES),
    id='check_classes',
    name='Check Sunspace classes',
    replace_existing=True
)

@app.on_event("startup")
async def startup_event():
    """Start the scheduler when the application starts"""
    scheduler.start()
    logging.info(f"Started scheduler, checking every {CHECK_INTERVAL_MINUTES} minutes")
    # Run initial check
    check_classes()

@app.on_event("shutdown")
async def shutdown_event():
    """Shut down the scheduler when the application stops"""
    scheduler.shutdown()
    logging.info("Scheduler shut down")

@app.get("/")
async def root():
    """Root endpoint showing service status"""
    return {
        "status": "running",
        "check_interval": f"{CHECK_INTERVAL_MINUTES} minutes",
        "notification_email": NOTIFICATION_EMAIL
    }

@app.get("/check-now")
async def check_now():
    """Endpoint to trigger an immediate check"""
    try:
        check_classes()
        return {"message": "Check completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 