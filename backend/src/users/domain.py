import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from ..common.exceptions import UserAlreadyExistsError
from ..database.crud import get_user_by_email, get_user_by_username

logger = logging.getLogger("hem_tracker")

def validate_as_new_user(db: Session, username: str, email: Optional[str] = None) -> None:
    logger.debug(f"Validate {username }as a new user ")
    if get_user_by_username(db, username):
        logger.error(f"Username {username} already registered")
        raise UserAlreadyExistsError("Username already registered")

    if email and get_user_by_email(db, email):
        logger.error(f"Email {email} already registered")
        raise UserAlreadyExistsError("Email already registered")


def format_weekly_infusions(infusions: List[str]) -> str:
    return ", ".join(infusions)
