import logging
from typing import Type

import numpy as np
from fastapi import HTTPException
from sqlalchemy.orm import Session

from . import domain
from . import schemas
from . import crud
from .schemas import UserSignup, UserUpdate, UserDelete, UserPlotData, UserDataResponse
from ..common.exceptions import DatabaseError, UserNotFoundException, UserAlreadyExistsError
from ..common.utils import calculate_decay_constant
from ..database.crud import update_user_by_username, get_user_by_username, delete_user_measurements, \
    delete_user_password_tokens, get_user_measurement
from ..database.models import Measurement
from ..measurement.schemas import UserMeasurements
from ...app.logging_config import setup_logging

setup_logging()

logger = logging.getLogger("hem_tracker")


def signup_new_user(db: Session, user_data: UserSignup) -> None:
    try:
        domain.validate_as_new_user(db, user_data.username, user_data.email)

        formatted_infusions = domain.format_weekly_infusions(
            user_data.weekly_infusions
        )

        new_user = schemas.UserCreate(
            username=user_data.username,
            password=user_data.password,
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            peak_level=user_data.peak_level,
            weekly_infusions=formatted_infusions,
        )

        crud.create_user(db=db, user=new_user)
    except UserAlreadyExistsError as exc:
        logger.error(f"Username or email already registered for user {user_data.username}: {str(exc)}")
        raise
    except Exception as exc:
        logger.error(f"Error while registering user {user_data.username} with email {user_data.email}: {str(exc)}")
        raise DatabaseError from exc


def edit_user_data(db: Session, user: UserUpdate) -> None:
    try:
        update_user_by_username(db=db, user_update=user)
    except UserNotFoundException as exc:
        logger.error(f"Error while updating the user info: {exc}")
        raise exc
    except Exception as exc:
        logger.error(f"Error while updating the user info: {exc}")
        raise RuntimeError("An unexpected error occurred while updating the user info")


def delete_user_and_measurements_by_username(db: Session, user: UserDelete):
    logger.debug(f"Attempt to delete user and measurements: {user.username}")
    db_user = get_user_by_username(db=db, username=user.username)
    if db_user:
        delete_user_measurements(db=db, user=db_user)
        delete_user_password_tokens(db, db_user)
        db.delete(db_user)
        db.commit()
        logger.debug(f"Deleted user and all measurements: {user}")
        return True
    return False


def delete_user(db: Session, username: str) -> None:
    try:
        user = get_user_by_username(db=db, username=username)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User with username {username} not found"
            )
        delete_user_measurements(db, user)
        delete_user_password_tokens(db, user)
        db.delete(user)
        db.commit()
        logger.info(f"Successfully deleted user: {username}")
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        logger.error(f"Error deleting user {username}: {str(exc)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while deleting the user"
        )


def get_user_data(db: Session, username: str) -> UserDataResponse:
    try:
        user = get_user_by_username(db=db, username=username)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User with username {username} not found"
            )
        return user
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        logger.error(f"Error getting data for user {username}: {str(exc)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while getting user data the user"
        )


def get_user_plot_data(db: Session, username: str) -> UserPlotData:
    try:
        user = get_user_by_username(db, username)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User with username {username} not found"
            )
        measurements = get_user_measurement(db=db, user_id=user.id)
        decay_constants = [calculate_decay_constant(measurement.peak_level, measurement.second_level_measurement,
                                                    measurement.time_elapsed) for measurement in
                           measurements]
        mean_decay_constant = np.mean(decay_constants)
        peak_level = user.peak_level
        weekly_infusions_list = user.weekly_infusions.split(", ") if user.weekly_infusions else []

        return UserPlotData(
            username=username,
            decay_constant=mean_decay_constant,
            peak_level=peak_level,
            weekly_infusions=weekly_infusions_list,
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error get user data user {username}: {str(exc)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while deleting the user"
        )


def get_user_measurements(db: Session, username: str) -> list[UserMeasurements]:
    try:
        logger.debug(f"Attempt to read user measurement for user: {username}")
        user = get_user_by_username(db, username)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User with username {username} not found"
            )
        measurements = get_user_measurement(db=db, user_id=user.id)

        return [UserMeasurements.from_orm(measurement) for measurement in measurements]

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error getting the user measurement for user {username}: {str(exc)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while getting the user measurement"
        )
