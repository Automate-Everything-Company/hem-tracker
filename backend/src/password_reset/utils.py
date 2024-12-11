import json
import logging
from typing import Dict

import requests

from backend.src.common.logging_config import setup_logging
from backend.src.core.config import SMTP2GO_KEY, SMTP2GO_URL

setup_logging()

logger = logging.getLogger("hem_tracker")

PASSWORD_RESET_URL = "https://hem-tracker.com/api/password/reset-password/"


def send_reset_email(email: str, token: str):
    body = generate_email_body(email, token)
    if not body:
        raise ValueError("Email body not generated")

    try:
        response = requests.post(SMTP2GO_URL, data=json.dumps(body["payload"]), headers=body["headers"])
        response.raise_for_status()
        result = response.json()
        if result.get("data", {}).get("succeeded", 0) > 0:
            logger.debug(f"Password reset email sent successfully to {email}")
        else:
            error_msg = result.get("error", "Unknown error")
            logger.error(f"Failed to send password reset email to {email}: {error_msg}")
            raise RuntimeError(f"Failed to send password reset email: {error_msg}")

    except requests.exceptions.RequestException as exc:
        logger.error(f"An error occurred while sending the password reset email: {str(exc)}")
        raise RuntimeError(f"An error occurred while sending the password reset email: {exc}") from exc

    except (ValueError, IndexError) as exc:
        logger.error(f"Error generating email content: {exc}")
        raise RuntimeError(f"Error generating email content: {exc}") from exc


def generate_email_body(email, token) -> dict[str, dict[str, str]]:
    reset_link = f"{PASSWORD_RESET_URL}{token}"
    logger.debug(f"Send link to email {email}: {reset_link}")
    content = generate_email_content(reset_link=reset_link)
    payload = generate_payload(email=email, content=content, link=reset_link)
    headers = generate_headers(api_key=SMTP2GO_KEY)
    return {"headers": headers, "payload": payload}


def generate_email_content(reset_link: str) -> str:
    if not reset_link:
        raise ValueError("No reset link provided")
    return f"""
        <html>
        <body>
        <p>Click the following link to reset your password:</p>
        <p><a href="{reset_link}">Link</a></p>
        </body>
        </html>
        """


def generate_payload(email: str, content: str, link: str) -> Dict[str, str]:
    return {
        "api_key": SMTP2GO_KEY,
        "to": [email],
        "sender": "info@automate-everything-company.com",
        "subject": "Password Reset",
        "html_body": content,
        "text_body": f"Click the following link to reset your password: {link}"
    }


def generate_headers(api_key: str) -> Dict[str, str]:
    return {
        "Content-Type": "application/json",
        "X-Smtp2go-Api-Key": api_key
    }
