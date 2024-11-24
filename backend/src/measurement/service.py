import logging

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.logging_config import setup_logging
from backend.src.common.utils import calculate_decay_constant, calculate_halving_time
from backend.src.database.crud import get_user_by_username
from backend.src.measurement.crud import save_measurement
from backend.src.measurement.schemas import MeasurementCreate, MeasurementResponse, MeasurementRequest

setup_logging()

logger = logging.getLogger("hem_tracker")


def create_user_measurement(db: Session, username: str, measurement: MeasurementRequest) -> MeasurementCreate:
    logger.debug(f"Attempt to create measurement for user: {username}")
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User with username {username} not found"
        )

    decay_constant = calculate_decay_constant(peak_level=measurement.peak_level,
                                              measured_level=measurement.second_level_measurement,
                                              time_elapsed=measurement.time_elapsed)
    logger.debug(f"Calculated decay constant for measurement for user {username}: {decay_constant}")

    halving_time = calculate_halving_time(decay_constant=decay_constant)
    logger.debug(f"Calculate halving time for measurement for user {username}: {halving_time}")

    new_measurement = MeasurementCreate(
        user_id=user.id,
        peak_level=measurement.peak_level,
        time_elapsed=measurement.time_elapsed,
        second_level_measurement=measurement.second_level_measurement,
        decay_constant=decay_constant,
        halving_time=halving_time,
        comment=measurement.comment
    )
    save_measurement(db=db, measurement=new_measurement)
    return new_measurement
