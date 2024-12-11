import logging

from fastapi import APIRouter, Depends, Path, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from starlette.requests import Request


from .schemas import UserUpdate, UserResponse, UserDataResponse, UserPlotData
from .service import edit_user_data, delete_user, get_user_data, \
    get_user_plot_data
from ..authentication.domain import verify_token
from ..common.exceptions import UserNotFoundException
from ..core.config import TEMPLATES
from ..database.crud import get_user_by_username
from ..database.dependencies import get_db
from backend.src.common.logging_config import setup_logging

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

setup_logging()

logger = logging.getLogger("hem_tracker")

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    responses={
        404: {"description": "User not found"},
        500: {"description": "Internal server error"}
    },
)


@router.put("/", response_model=UserResponse)
def edit_user(user: UserUpdate, db: Session = Depends(get_db)) -> UserResponse:
    try:
        edit_user_data(db=db, user=user)
        return UserResponse(message="User info updated", success=True)
    except UserNotFoundException as exc:
        logger.error(f"Error while editing user data: {exc}")
        return UserResponse(message="User not found", success=False)
    except RuntimeError as exc:
        logger.error(f"Runtime error: {exc}")
        return UserResponse(message="An error occurred while updating the user", success=False)


@router.delete("/{username}", response_model=UserResponse)
def delete_user_endpoint(
        username: str = Path(..., description="Username to delete"),
        db: Session = Depends(get_db)
) -> UserResponse:
    delete_user(db=db, username=username)
    return UserResponse(
        message=f"User {username} successfully deleted",
        success=True
    )


@router.get("/{username}/data", response_model=UserDataResponse)
def get_data(username: str, db: Session = Depends(get_db)):
    user = get_user_data(db=db, username=username)
    return user


@router.get("/user-data/{username}", response_model=UserPlotData)
def user_plot_data(username: str, db: Session = Depends(get_db)):
    user_data = get_user_plot_data(db=db, username=username)
    return user_data


@router.get("/{username}", response_class=HTMLResponse)
def read_user_page(username: str, request: Request, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_token(token)
    if username != payload.get("sub"):
        raise HTTPException(status_code=403, detail="Not authorized to access this user's data")
    db_user = get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    html_content = TEMPLATES.TemplateResponse("user.html", {"request": request, "user": db_user}).body.decode('utf-8')
    return HTMLResponse(content=html_content)
