import logging
import traceback
from typing import Type

import sqlalchemy
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.src.common.logging_config import setup_logging
from backend.src.database.models import Measurement
from backend.src.measurement.schemas import MeasurementCreate, MeasurementDelete

setup_logging()

logger = logging.getLogger("hem_tracker")


def save_measurement(db: Session, measurement: MeasurementCreate) -> Measurement:
    try:
        db_measurement = Measurement(
            user_id=measurement.user_id,
            peak_level=measurement.peak_level,
            time_elapsed=measurement.time_elapsed,
            second_level_measurement=measurement.second_level_measurement,
            decay_constant=measurement.decay_constant,
            halving_time=measurement.halving_time,
            comment=measurement.comment
        )
        db.add(db_measurement)
        db.commit()
        db.refresh(db_measurement)
        return db_measurement

    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        logger.debug(f"Integrity error: {e}")
    except sqlalchemy.exc.OperationalError as e:
        db.rollback()
        logger.debug(f"Operational error: {e}")
    except AttributeError as e:
        logger.debug(f"Attribute error: {e}")
    except Exception as e:
        db.rollback()
        logger.debug(f"Unexpected error: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")


def delete(db: Session, db_measurement: Type[Measurement] | list[Type[Measurement]]) -> MeasurementDelete:
    try:
        db.delete(db_measurement)
        db.commit()
        db.refresh(db_measurement)
        measurement = MeasurementDelete(
            id=db_measurement.id,
            user_id=db_measurement.user_id
        )
        return measurement
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        logger.debug(f"Integrity error: {e}")
    except sqlalchemy.exc.OperationalError as e:
        db.rollback()
        logger.debug(f"Operational error: {e}")
    except AttributeError as e:
        logger.debug(f"Attribute error: {e}")
    except Exception as e:
        db.rollback()
        logger.debug(f"Unexpected error: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")


def get_measurement(db: Session, measurement_id: int) -> Type[Measurement] | list[
    Type[Measurement]]:
    db_measurement = db.query(Measurement).filter(Measurement.id == measurement_id).first()

    if not db_measurement:
        raise HTTPException(status_code=404, detail="No measurement found")
    return db_measurement
