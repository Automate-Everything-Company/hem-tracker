import os
from datetime import timedelta, datetime
from typing import Dict

from passlib.context import CryptContext
from jose import jwt

from backend.src.core.config import ALGORITHM

SECRET_KEY = os.getenv("SECRET_KEY")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: Dict[str, str | datetime], minutes: float = 15):
    to_encode = data.copy()
    if not to_encode['exp']:
        expire = datetime.utcnow() + timedelta(minutes=minutes)
        to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def is_password_valid(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
