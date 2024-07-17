import logging
import os

import requests
import json
from dotenv import load_dotenv

logger = logging.getLogger("hem_tracker")

load_dotenv()

SMTP2GO_KEY = os.getenv("SMTP2GO_KEY")


def send_reset_email(email: str, token: str):
    api_url = "https://api.smtp2go.com/v3/email/send"

    api_key = SMTP2GO_KEY

    reset_link = f"https://hem-tracker/reset-password/{token}"
    logger.debug(f"Send link to email {email}: {reset_link}")

    email_content = f"""
    <html>
    <body>
    <p>Click the following link to reset your password:</p>
    <p><a href="{reset_link}">Link</a></p>
    </body>
    </html>
    """

    payload = {
        "api_key": api_key,
        "to": [email],
        "sender": "info@automate-everything-company.com",
        "subject": "Password Reset",
        "html_body": email_content,
        "text_body": f"Click the following link to reset your password: {reset_link}"
    }

    headers = {
        "Content-Type": "application/json",
        "X-Smtp2go-Api-Key": api_key
    }

    try:
        response = requests.post(api_url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()

        result = response.json()
        if result.get("data", {}).get("succeeded", 0) > 0:
            logger.debug(f"Password reset email sent successfully to {email}")
        else:
            logger.debug(f"Failed to send password reset email to {email}")
            logger.debug(f"Error: {result.get('error', 'Unknown error')}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while sending the password reset email: {str(e)}")
