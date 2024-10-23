from typing import Type, Any, Optional

from fastapi import HTTPException
from sqlalchemy import literal
from sqlalchemy.orm import Session

from backend.src.database.models import Measurement, User, PasswordResetToken


def get_user(db: Session, username: str) -> Any:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="No user found.")
    return user


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_measurement_values(db: Session, user_id: int, measurement_id: int) -> Type[Measurement]:
    measurements = db.query(Measurement).filter(Measurement.user_id == user_id).all()
    if not measurements:
        raise HTTPException(status_code=404, detail="No measurements found.")
    return measurements[measurement_id]


def save_reset_token(db: Session, user_id: int, reset_token: str) -> str:
    db_token = PasswordResetToken(user_id=user_id, token=reset_token)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token


def get_user_by_reset_token(db: Session, token: str):
    db_token = db.query(PasswordResetToken).filter(PasswordResetToken.token == token).first()
    if db_token:
        return db.query(User).filter(User.id == literal(db_token.user_id)).first()
    return None

