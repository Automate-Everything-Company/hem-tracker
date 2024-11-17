import logging
from typing import List

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from .schemas import UserDelete, UserUpdate, UserResponse, UserDataResponse, UserPlotData, UserMeasurements
from .service import edit_user_data, delete_user_and_measurements_by_username, delete_user, get_user_data, \
    get_user_plot_data, get_user_measurements
from ..common.exceptions import UserNotFoundException
from ..database.dependencies import get_db
from ..database.models import User, Measurement
from ...app.logging_config import setup_logging

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


@router.get("/{username}/measurements/", response_model=list[UserMeasurements])
def user_measurements(username: str, db: Session = Depends(get_db)):
    measurements = get_user_measurements(db=db, username=username)
    return measurements

#
# @router.post("/users/{username}/measurements/", response_model=schemas.MeasurementCreate)
# def create_measurement(username: str, measurement: schemas.MeasurementCreate, db: Session = Depends(get_db)):
#     logger.debug(f"Attempt to create measurement for user: {username}")
#     db_user = db.query(models.User).filter(models.User.username == username).first()
#     if db_user is None:
#         logger.debug(f"User not found: {username}")
#         raise HTTPException(status_code=404, detail="User not found")
#
#     decay_constant = calculate_decay_constant(peak_level=measurement.peak_level,
#                                               measured_level=measurement.second_level_measurement,
#                                               time_elapsed=measurement.time_elapsed)
#     logger.debug(f"Calculate decay constant for measurement for user {username}: {decay_constant}")
#     halving_time = calculate_halving_time(decay_constant=decay_constant)
#     logger.debug(f"Calculate halving time for measurement for user {username}: {halving_time}")
#
#     try:
#         db_measurement = models.Measurement(
#             user_id=db_user.id,
#             peak_level=measurement.peak_level,
#             time_elapsed=measurement.time_elapsed,
#             second_level_measurement=measurement.second_level_measurement,
#             decay_constant=decay_constant,
#             halving_time=halving_time,
#             comment=measurement.comment
#         )
#         db.add(db_measurement)
#         db.commit()
#         db.refresh(db_measurement)
#         return db_measurement
#
#     except sqlalchemy.exc.IntegrityError as e:
#         db.rollback()
#         logger.debug(f"Integrity error: {e}")
#     except sqlalchemy.exc.OperationalError as e:
#         db.rollback()
#         logger.debug(f"Operational error: {e}")
#     except AttributeError as e:
#         logger.debug(f"Attribute error: {e}")
#     except Exception as e:
#         db.rollback()
#         logger.debug(f"Unexpected error: {e}")
#         logger.debug(f"Traceback: {traceback.format_exc()}")
#
#
# @app.post("/users/{username}/measurements", include_in_schema=False)
# async def redirect_measurements(username: str):
#     return RedirectResponse(url=f"/users/{username}/measurements/", status_code=307)
#
#
# @app.delete("/users/{username}/measurements/{measurement_id}", response_model=schemas.Measurement)
# def delete_measurement(username: str, measurement_id: int, db: Session = Depends(get_db)):
#     db_user = db.query(models.User).filter(models.User.username == username).first()
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     db_measurement = db.query(models.Measurement).filter(models.Measurement.id == measurement_id).first()
#     if db_measurement is None:
#         raise HTTPException(status_code=404, detail="Measurement not found")
#
#     db.delete(db_measurement)
#     db.commit()
#     return db_measurement
#
#
# @app.get("/users/")
# def read_user(email: str, request: Request, db: Session = Depends(get_db)):
#     db_user = crud.get_user_by_email(db, email=email)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return templates.TemplateResponse("user.html", {"request": request, "user": db_user})
#
#
# @app.get("/user/{username}", response_class=HTMLResponse)
# def read_user_page(username: str, request: Request, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     payload = verify_token(token)
#     if username != payload.get("sub"):
#         raise HTTPException(status_code=403, detail="Not authorized to access this user's data")
#     db_user = crud.get_user_by_username(db, username=username)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     # Render the template to a string
#     html_content = templates.TemplateResponse("user.html", {"request": request, "user": db_user}).body.decode('utf-8')
#     return HTMLResponse(content=html_content)
