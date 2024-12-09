import logging

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from starlette import status
from starlette.requests import Request
from starlette.responses import HTMLResponse

from .service import request_password_reset
from ..common.exceptions import UserNotFoundException, InvalidTokenException, EmailSendingFailedException
from ..core.config import TEMPLATES
from backend.src.common.logging_config import setup_logging

from backend.src.database.dependencies import get_db
from backend.src.password_reset.schemas import PasswordResetRequest, PasswordResetResponse
from ..database.crud import get_user_by_reset_token

setup_logging()

logger = logging.getLogger("hem_tracker")

router = APIRouter(
    prefix="/api/password",
    tags=["password", "password-reset"],
    responses={
        403: {"description": "Operation forbidden"},
        404: {"description": "Not Found"},
        500: {"description": "Server error"},
    })


@router.post("/request-reset")
def send_password_reset_link(request: PasswordResetRequest, db: Session = Depends(get_db)) -> PasswordResetResponse:
    try:
        request_password_reset(identifier=request.identifier, db=db)
        return PasswordResetResponse(
            message="If your email or username is registered, you will receive reset instructions.")
    except UserNotFoundException:
        return PasswordResetResponse(
            message="If your email or username is registered, you will receive reset instructions.")
    except EmailSendingFailedException:
        logger.error(f"Failed to send password reset email to identifier: {request.identifier}")
        return PasswordResetResponse(message="Failed to send password reset email. Please try again later.")
    except Exception as exc:
        logger.exception(f"Unexpected error during password reset request: {exc}")
        return PasswordResetResponse(message="An unexpected error occurred. Please try again later.")


@router.get(
    "/reset-password/{token}",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset password page",
    description="Render the password reset page if the token is valid.",
)
async def reset_password_page(request: Request, token: str, db: Session = Depends(get_db)):
    try:
        user = get_user_by_reset_token(db=db, token=token)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        return TEMPLATES.TemplateResponse("reset_password.html", {"request": request, "token": token})

    except InvalidTokenException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except UserNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(f"Error rendering reset password page: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
