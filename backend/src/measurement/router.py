import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from .schemas import MeasurementCreate, MeasurementRequest, UserMeasurements, MeasurementDelete
from .service import create_user_measurement, delete_measurement
from ..database.dependencies import get_db
from ..users.service import get_user_measurements
from backend.src.common.logging_config import setup_logging

setup_logging()

logger = logging.getLogger("hem_tracker")

router = APIRouter(
    prefix="/api/measurement",
    tags=["measurement"],
    responses={
        404: {"description": "Measurement not found"},
        500: {"description": "Internal server error"}
    },
)


@router.get("/{username}/measurements/", response_model=list[UserMeasurements])
def user_measurements(username: str, db: Session = Depends(get_db)):
    measurements = get_user_measurements(db=db, username=username)
    return measurements


@router.post("/{username}/measurements/", response_model=MeasurementCreate)
def create_measurement(username: str, measurement: MeasurementRequest, db: Session = Depends(get_db)):
    return create_user_measurement(db=db, username=username, measurement=measurement)


@router.post("/measurement/{username}/measurements", include_in_schema=False)
async def redirect_measurements(username: str):
    return RedirectResponse(url=f"/measurement/{username}/measurements/", status_code=307)


@router.delete("/{username}/measurements/{measurement_id}", response_model=MeasurementDelete)
def delete(username: str, measurement_id: int, db: Session = Depends(get_db)):
    deleted_measurement = delete_measurement(db=db, measurement_id=measurement_id)
    return deleted_measurement

