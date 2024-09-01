import logging
from math import exp, isclose
from typing import List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from fastapi import FastAPI, APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from sqlalchemy.orm import Session

import numpy as np
import pytz

from ... import schemas, crud
from ...calculations import calculate_decay_constant, calculate_halving_time
from ...dependencies import get_db
from ...schemas import DefaultValues, DecayConstantParameters

CET = pytz.timezone('Europe/Berlin')

NOW = datetime.now(CET)
CURRENT_YEAR = NOW.year
CURRENT_MONTH = NOW.month

app = FastAPI()


logger = logging.getLogger("hem_tracker")


class FactorLevelSettings(BaseModel):
    initial_factor_level: Optional[float] = Field(..., alias='peakLevel')
    decay_constant: Optional[float] = Field(..., alias='decayConstant')
    refill_times: Optional[List[str]] = Field(..., alias='refillTimes')
    current_level: Optional[str] = Field(..., alias='currentTime')

    class Config:
        populate_by_name = True


@dataclass
class FactorCalculationParameters:
    initial_factor_level: float
    decay_constant: float
    refill_hours: List[float]
    week_duration: int


router = APIRouter()


def convert_to_datetime(date_str):
    time_part = ' '.join(date_str.split()[1:])  # Gets "10:05 AM"
    datetime_obj = datetime.strptime(time_part, '%I:%M %p')
    datetime_obj = datetime_obj.replace(year=CURRENT_YEAR, month=CURRENT_MONTH)

    weekday_str = date_str.split()[0]  # Gets "Monday"
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    target_weekday = weekdays.index(weekday_str)
    current_weekday = NOW.weekday()

    days_difference = target_weekday - current_weekday
    correct_date = NOW + timedelta(days=days_difference)

    final_datetime = datetime_obj.replace(day=correct_date.day)

    return CET.localize(final_datetime)


def generate_refill_hours(refill_times: List[str], start_of_week: datetime) -> List[float]:
    refill_times_in_datetime_format = generate_refill_times_in_datetime_format(refill_times, start_of_week)
    refill_hours = generate_refill_times_in_hour_format(refill_times_in_datetime_format, start_of_week)
    return refill_hours


def generate_refill_times_in_hour_format(refill_times_in_datetime_format, start_of_week):
    refill_hours_in_numbers = []
    for refill_time_in_datetime in refill_times_in_datetime_format:
        refill_time_in_hour = float(f"{(refill_time_in_datetime - start_of_week).total_seconds() / 3600:.1f}") # one decimal float
        refill_hours_in_numbers.append(refill_time_in_hour)
    return refill_hours_in_numbers


def generate_refill_times_in_datetime_format(refill_times, start_of_week):
    refill_datetimes = []

    for time_str in refill_times:
        refill_time_in_datetime = parse_refill_time(time_str, start_of_week)
        refill_datetimes.append(refill_time_in_datetime)

    return refill_datetimes


def parse_refill_time(time_str: str, start_of_week: datetime) -> datetime:
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_part, *time_part = time_str.split()
    day_of_week = weekdays.index(day_part)
    time_part = " ".join(time_part)
    time_obj = datetime.strptime(time_part, "%I:%M %p")
    time_obj = time_obj.replace(year=CURRENT_YEAR, month=CURRENT_MONTH)
    day_datetime = start_of_week + timedelta(days=day_of_week)
    return day_datetime.replace(hour=time_obj.hour, minute=time_obj.minute)


def calculate_levels(week_hours: List[float], params: FactorCalculationParameters) -> List[float]:
    levels = []
    peak_value = params.initial_factor_level

    for hour in week_hours:
        if not params.refill_hours:
            levels.append(0.0)
            continue

        if hour < params.refill_hours[0]:
            previous_week_last_refill = params.refill_hours[-1] - params.week_duration
            factor_value = params.initial_factor_level * exp(params.decay_constant * (hour - previous_week_last_refill))
            levels.append(factor_value)
            continue

        for i in range(len(params.refill_hours)):
            if isclose(hour, params.refill_hours[i]):
                if i == 0:
                    previous_week_last_refill = params.refill_hours[-1] - params.week_duration
                    previous_hour = hour - 0.1
                    previous_level_value = peak_value * exp(
                        params.decay_constant * (previous_hour - previous_week_last_refill))
                    level_value = params.initial_factor_level + previous_level_value
                    peak_value = level_value
                    levels.append(level_value)
                else:
                    previous_hour = hour - 0.1
                    last_refill_hour = params.refill_hours[i - 1]
                    previous_value = peak_value * exp(params.decay_constant * (previous_hour - last_refill_hour))
                    level_value = params.initial_factor_level + previous_value
                    peak_value = level_value
                    levels.append(level_value)
                break

            if hour < params.refill_hours[i]:
                if i == 0:
                    previous_week_last_refill = params.refill_hours[-1] - params.week_duration
                    level_value = params.initial_factor_level * exp(
                        params.decay_constant * (hour - previous_week_last_refill))
                    levels.append(level_value)
                else:
                    level_value = peak_value * exp(params.decay_constant * (hour - params.refill_hours[i - 1]))
                    levels.append(level_value)
                break

        if hour > params.refill_hours[-1]:
            levels.append(peak_value * exp(params.decay_constant * (hour - params.refill_hours[-1])))

    return levels


@router.post("/update-factor-levels", response_model=dict)
async def get_factor_levels(settings: FactorLevelSettings) -> dict:
    try:
        logger.debug("Try to update factor levels")
        logger.debug(f"Settings: {settings}")
        hours_in_a_week = 24 * 7

        start_of_week = CET.localize(
            datetime.combine(datetime.now(CET).date() - timedelta(days=datetime.now(CET).date().weekday()),
                             datetime.min.time()))
        logger.debug(f"Start of the week: {start_of_week}")
        decay_constant = settings.decay_constant
        halving_time = calculate_halving_time(decay_constant=decay_constant)

        refill_hours = generate_refill_hours(settings.refill_times, start_of_week)
        logger.debug(f"Refill hours: {refill_hours}")
        week_hours = np.arange(0, hours_in_a_week, 0.1).round(2)
        week_hours = week_hours.tolist()

        level_params = FactorCalculationParameters(
            refill_hours=refill_hours,
            initial_factor_level=settings.initial_factor_level,
            decay_constant=decay_constant,
            week_duration=hours_in_a_week
        )
        logger.debug(f"Level params: {level_params}")
        levels = calculate_levels(week_hours=week_hours, params=level_params)
        current_time = convert_to_datetime(settings.current_level)
        current_hour = (current_time - start_of_week).total_seconds() / 3600
        current_hour = float(f"{current_hour:.1f}")
        current_factor_level = levels[week_hours.index(current_hour)]
        result = {
            "hours": week_hours,
            "start_of_week": start_of_week.isoformat(),
            "levels": levels,
            "current_time": current_time.isoformat(),
            "current_factor_level": [current_hour, current_factor_level],
            "halving_time": halving_time
        }
        logger.debug(f"Return result start of week: {start_of_week.isoformat()}")
        logger.debug(f"Return result current time: {current_time.isoformat()}")
        logger.debug(f"Return result current factor level: {[current_hour, current_factor_level]}")
        logger.debug(f"Return result halving time: {[halving_time]}")
        return result
    except Exception as exc:
        logger.error(exc, exc_info=True)


@router.post("/calculate-decay-constant", response_model=dict)
async def get_factor_levels(measurement: DecayConstantParameters) -> dict:
    decay_constant = calculate_decay_constant(peak_level=measurement.peak_level,
                                              measured_level=measurement.second_level_measurement,
                                              time_elapsed=measurement.time_elapsed)

    return {
        "decay_constant": decay_constant,
    }


@router.get("/default-values", response_model=DefaultValues)
async def get_default_values(db: Session = Depends(get_db)):
    username = "stefanjosan"
    measurement_id = 0

    db_user = crud.get_user_by_username(db, username)
    measurement = crud.get_measurement_values(db=db, user_id=db_user.id, measurement_id=measurement_id)

    if measurement:
        peak_level = measurement.peak_level
        time_elapsed = measurement.time_elapsed
        second_level_measurement = measurement.second_level_measurement
        decay_constant = calculate_decay_constant(peak_level=measurement.peak_level,
                                                  measured_level=measurement.second_level_measurement,
                                                  time_elapsed=measurement.time_elapsed)

        default_values = DefaultValues()
        default_values.decay_constant = decay_constant
        default_values.peak_level = peak_level
        default_values.time_elapsed = time_elapsed
        default_values.second_level_measurement = second_level_measurement
        default_values.refill_times = db_user.weekly_infusions.split(", ")
        return default_values
    raise HTTPException(status_code=404, detail="Measurement not found")


app.include_router(router)
