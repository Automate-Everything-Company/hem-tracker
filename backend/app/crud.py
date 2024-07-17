from typing import Union, List

import numpy as np
from fastapi import HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from . import models, schemas
from .calculations import calculate_decay_constant

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        password=hashed_password,
        email=user.email,
        peak_level=user.peak_level,
        weekly_infusions=user.weekly_infusions
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_default_values(db: Session, username: str) -> Union[schemas.UserSignup, None]:
    db_user = get_user_by_username(db, username)
    if db_user:
        weekly_infusions_list = db_user.weekly_infusions.split(", ") if db_user.weekly_infusions else []
        return schemas.UserSignup(
            first_name=db_user.first_name,
            last_name=db_user.last_name,
            username=db_user.username,
            password=db_user.password,
            email=db_user.email,
            peak_level=db_user.peak_level,
            weekly_infusions=weekly_infusions_list
        )
    return None


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def delete_user_and_measurements_by_username(db: Session, username: str):
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if db_user:
        delete_user_measurements(db, db_user)
        db.delete(db_user)
        db.commit()
        return True
    return False


def delete_user_measurements(db: Session, db_user: models.User):
    measurements = db_user.measurements
    for measurement in measurements:
        db.delete(measurement)


def delete_user_by_email(db: Session, email: str):
    db_user = db.query(models.User).filter(models.User.email == email).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False


def get_user_plot_data(db: Session, username: str) -> Union[None, schemas.UserPlotsData]:
    db_user = get_user_by_username(db, username)

    if db_user:
        measurements = db.query(models.Measurement).filter(models.Measurement.user_id == db_user.id).all()
        if not measurements:
            raise HTTPException(status_code=404, detail="No measurements found for this user.")

        decay_constants = [calculate_decay_constant(m.peak_level, m.second_level_measurement, m.time_elapsed) for m in
                           measurements]
        decay_constant = np.mean(decay_constants)

        peak_level = db_user.peak_level
        weekly_infusions_list = db_user.weekly_infusions.split(", ") if db_user.weekly_infusions else []

        return schemas.UserPlotsData(
            decay_constant=decay_constant,
            peak_level=peak_level,
            refillTimes=weekly_infusions_list,
            currentTime=""
        )
    return None


def create_measurement(db: Session, measurement: schemas.MeasurementCreate, user_id: int):
    decay_constant = calculate_decay_constant(measurement.peak_level, measurement.second_level_measurement,
                                              measurement.time_elapsed)
    db_measurement = models.Measurement(
        user_id=user_id,
        peak_level=measurement.peak_level,
        time_elapsed=measurement.time_elapsed,
        second_level_measurement=measurement.second_level_measurement,
        decay_constant=decay_constant,
        comment=measurement.comment
    )
    db.add(db_measurement)
    db.commit()
    db.refresh(db_measurement)
    return db_measurement


def get_measurements(db: Session, user_id: int) -> List[models.Measurement]:
    measurements = db.query(models.Measurement).filter(models.Measurement.user_id == user_id).all()
    if not measurements:
        raise HTTPException(status_code=404, detail="No measurements found for this user.")
    return measurements


def calculate_mean_decay_constant(db: Session, user_id: int) -> float:
    measurements = get_measurements(db=db, user_id=user_id)
    decay_constants = []
    for m in measurements:
        decay_constant = calculate_decay_constant(m.peak_level, m.second_level_measurement,
                                                  m.time_elapsed)
        decay_constants.append(decay_constant)
    mean_decay_constant = np.mean(decay_constants)

    return float(mean_decay_constant)


def get_measurement_values(db: Session, user_id: int, measurement_id: int) -> float:
    measurements = get_measurements(db=db, user_id=user_id)
    return measurements[measurement_id]


def update_user(db: Session, db_user: models.User, user_update: schemas.UserUpdate) -> models.User:
    db_user.email = user_update.email
    db_user.first_name = user_update.first_name
    db_user.last_name = user_update.last_name
    db_user.peak_level = user_update.peak_level
    db_user.weekly_infusions = ", ".join(user_update.weekly_infusions)
    db.commit()
    db.refresh(db_user)
    return db_user


def save_reset_token(db: Session, user_id: int, reset_token: str):
    db_token = models.PasswordResetToken(user_id=user_id, token=reset_token)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token


def get_user_by_reset_token(db: Session, token: str):
    db_token = db.query(models.PasswordResetToken).filter(models.PasswordResetToken.token == token).first()
    if db_token:
        return db.query(models.User).filter(models.User.id == db_token.user_id).first()
    return None


def update_user_password(db: Session, user_id: int, new_password: str):
    hashed_password = pwd_context.hash(new_password)
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    db_user.password = hashed_password
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_reset_token(db: Session, token: str):
    db.query(models.PasswordResetToken).filter(models.PasswordResetToken.token == token).delete()
    db.commit()
