from datetime import timedelta, datetime
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status
from jose import jwt, JWTError

from backend.constants.constants import HOUR_IN_SECONDS, ACCESS_TOKEN_EXPIRE_MINUTES
from backend.src.authentication.schemas import Token
from backend.src.common.security import create_access_token, is_password_valid
from backend.src.core.config import SECRET_KEY, ALGORITHM
from backend.src.database.crud import get_user_by_username


def create_user_access_token(db: Session, username: str, password: str) -> Token:
    user = validate_user_credentials(db, password, username)
    token_data = create_token_data(user=user)
    access_token = create_access_token(data=token_data)

    return Token(access_token=access_token, expires_in=HOUR_IN_SECONDS, token_type="bearer")


def validate_user_credentials(db, password, username):
    user = get_user_by_username(db=db, username=username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not is_password_valid(plain_password=password, hashed_password=user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def create_token_data(user):
    token_data = {
        "sub": user.username,
        "user_id": user.id,
        "jti": str(uuid4()),
        "iat": datetime.utcnow(),
        "type": "access_token",
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return token_data


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
