import logging

from fastapi import Depends, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette import status

from backend.src.authentication.schemas import Token
from backend.src.common.logging_config import setup_logging
from backend.src.authentication.domain import create_user_access_token
from backend.src.database.dependencies import get_db
from backend.src.users.schemas import UserSignup, SignupResponse
from backend.src.users.service import signup_new_user

setup_logging()

logger = logging.getLogger("hem_tracker")

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/login",
    response_model=Token,
    summary="Create access token for user",
    response_description="Access token for authenticated user",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    try:
        logger.debug("Login endpoint accessed.")
        logger.info(f"Attempt to create access token for user  {form_data.username}.")
        access_token = create_user_access_token(db=db, username=form_data.username, password=form_data.password)
        return access_token
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login. Check if password is correct.",
        ) from exc


@router.post(
    "/signup",
    response_model=SignupResponse,
    summary="Registers a new user in the system",
    response_description="User successfully created",
)
def signup(user: UserSignup, db: Session = Depends(get_db)) -> SignupResponse:
    try:
        logger.debug("Sign up endpoint accessed.")
        logger.info(f"User {user} attempted to sign up.")
        signup_new_user(db, user)
        return SignupResponse(detail="Signup successful")
    except ValidationError as exc:
        logger.error(f"Validation error occurred: {str(exc)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        logger.error(f"Server error occurred: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during signup"
        )
