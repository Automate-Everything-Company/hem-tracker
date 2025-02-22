import logging
from typing import Type, Optional

from fastapi import HTTPException
from sqlalchemy import literal
from sqlalchemy.orm import Session

from backend.src.common.logging_config import setup_logging
from backend.src.database.models import Measurement, User, PasswordResetToken
from backend.src.users.schemas import UserUpdate, UserBase

setup_logging()

logger = logging.getLogger("hem_tracker")


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def update_user_by_username(db: Session, user_update: UserUpdate) -> UserBase:
    try:
        username = user_update.username
        db_user = get_user_by_username(db=db, username=username)
        if not db_user:
            logger.error(f"User update requested for non-existing user: {username}")
            raise HTTPException(
                status_code=404,
                detail=f"User with username {username} not found"
            )
        else:
            logger.debug(f"User found: {username}")

        if user_update.email:
            db_user.email = user_update.email
        if user_update.first_name:
            db_user.first_name = user_update.first_name
        if user_update.last_name:
            db_user.last_name = user_update.last_name
        if user_update.peak_level:
            db_user.peak_level = user_update.peak_level
        if user_update.weekly_infusions:
            db_user.weekly_infusions = ", ".join(user_update.weekly_infusions)
        db.commit()
        db.refresh(db_user)
        return db_user
    except HTTPException:
        logger.error(f"User with username {user_update.username} not found")
        raise
    except Exception as exc:
        db.rollback()
        logger.error(f"Error occured while updating info for user {user_update.username} because: {str(exc)}")


def get_user_measurement(db: Session, user_id: int, measurement_id: int = None) -> Measurement | list[
    Measurement]:
    measurements = db.query(Measurement).filter(Measurement.user_id == user_id).all()
    if measurement_id is not None:
        return measurements[measurement_id]
    return measurements


def save_reset_token(db: Session, user_id: int, reset_token: str) -> str:
    db_token = PasswordResetToken(user_id=user_id, token=reset_token)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token


def get_user_by_reset_token(db: Session, token: str):
    db_token = db.query(PasswordResetToken).filter(PasswordResetToken.token == token).first()
    if db_token:
        return db.query(User).filter(User.id == db_token.user_id).first()
    return None


def delete_user_measurements(db: Session, user: User) -> None:
    try:
        db.query(Measurement).filter(
            Measurement.user_id == user.id
        ).delete(synchronize_session=False)
    except Exception as e:
        logger.error(f"Error deleting measurements for user {user.id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete user measurements"
        )


def delete_user_password_tokens(db: Session, user: User) -> None:
    try:
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id
        ).delete(synchronize_session=False)
    except Exception as e:
        logger.error(f"Error deleting password tokens for user {user.id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete user password tokens"
        )
