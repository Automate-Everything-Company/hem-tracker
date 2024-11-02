import logging
import secrets

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.logging_config import setup_logging
from backend.src.common.exceptions import UserNotFoundException, EmailSendingFailedException
from backend.src.database.crud import get_user_by_email, get_user_by_username, save_reset_token
from backend.src.database.dependencies import get_db
from backend.src.password_reset.schemas import PasswordResetRequest, PasswordResetResult
from backend.src.password_reset.utils import send_reset_email

setup_logging()

logger = logging.getLogger("hem_tracker")


def request_password_reset(identifier: str, db: Session) -> PasswordResetResult:
    try:
        if "@" in identifier:
            user = get_user_by_email(db, email=identifier)
        else:
            user = get_user_by_username(db, username=identifier)

        if not user:
            logger.info(f"Password reset requested for non-existent identifier: {identifier}")
            raise UserNotFoundException()

        reset_token = secrets.token_urlsafe(32)
        save_reset_token(db=db, user_id=user.id, reset_token=reset_token)
        logger.debug(f"Generated reset token for user {user.email}")

        logger.debug(f"Attempting to send password reset email to user: {user.email}")
        send_reset_email(email=user.email, token=reset_token)

        return PasswordResetResult(
            success=True,
            message="An email with instructions was sent to your registered email adress"
        )
    except (RuntimeError, ValueError, IndexError) as exc:
        logger.error(f"Error during password reset request: {exc}")
        raise EmailSendingFailedException() from exc
