import logging
import traceback

import sqlalchemy
from sqlalchemy.orm import Session

from backend.app.logging_config import setup_logging
from backend.src.database.models import Measurement
from backend.src.measurement.schemas import MeasurementCreate

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
