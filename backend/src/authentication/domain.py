from datetime import timedelta, datetime
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from backend.app.crud import is_password_valid
from backend.constants.constants import HOUR_IN_SECONDS, ACCESS_TOKEN_EXPIRE_MINUTES
from backend.src.authentication.schemas import Token
from backend.src.common.security import create_access_token
from backend.src.database.crud import get_user, get_user_by_username


def create_user_access_token(db: Session, username: str, password: str) -> Token:
    user = get_user_by_username(db=db, username=username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if not is_password_valid(plain_password=password, hashed_password=user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token_data = {
        "sub": user.username,
        "user_id": user.id,
        "jti": str(uuid4()),
        "iat": datetime.utcnow(),
        "type": "access_token",
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }

    access_token = create_access_token(data=token_data)

    return Token(
        access_token=access_token,
        expires_in=HOUR_IN_SECONDS,
        token_type="bearer"
    )


class AuthService:  # rewrite as functions
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def authenticate_user(self, username: str, password: str) -> Token:
        user = get_user_by_username(db=self.db_session, username=username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        if not is_password_valid(plain_password=password, hashed_password=user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )

        token_data = {
            "sub": user.username,
            "user_id": user.id,
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        }

        access_token = create_access_token(
            data=token_data,
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

        return Token(
            access_token=access_token,
            expires_in=HOUR_IN_SECONDS,
            token_type="bearer"
        )
