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
    tags=["Authentication"],
    responses={
        401: {"description": "Unauthorized - Invalid credentials"},
        404: {"description": "Not Found - User not found"},
        422: {"description": "Validation Error - Invalid request format"},
        500: {"description": "Internal Server Error - Authentication service error"},
    },
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
        signup_new_user(db, user)
        return SignupResponse(detail="Signup successful")
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during signup"
        )
