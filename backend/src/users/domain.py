"""
Core business logic module.

Contains fundamental business rules and validations.
Independent of external services or application layers.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from ..common.exceptions import UserAlreadyExistsError
from ..database.crud import get_user_by_email, get_user_by_username


def validate_as_new_user(db: Session, username: str, email: Optional[str] = None) -> None:
    if get_user_by_username(db, username):
        raise UserAlreadyExistsError("Username already registered")

    if email and get_user_by_email(db, email):
        raise UserAlreadyExistsError("Email already registered")


def format_weekly_infusions(infusions: List[str]) -> str:
    return ", ".join(infusions)
