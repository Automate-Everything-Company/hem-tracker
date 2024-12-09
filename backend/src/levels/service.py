from math import exp, isclose
from typing import Dict, List

from fastapi import Depends
from sqlalchemy.orm import Session

from .models import FactorCalculationParameters
from .schemas import DefaultValues, FactorLevelSettings
from .utils import (
    get_start_of_the_week,
    create_week_hours,
    convert_to_datetime,
    generate_refill_hours
)
from ..common.utils import calculate_decay_constant, calculate_halving_time
from ..database.crud import get_user, get_user_measurement, get_user_by_username
from ..database.dependencies import get_db


def calculate_factor_levels(settings: FactorLevelSettings) -> Dict[str, str]:
    try:
        hours_in_a_week = 24 * 7

        start_of_week = get_start_of_the_week()

        halving_time = calculate_halving_time(decay_constant=settings.decay_constant)

        refill_hours = generate_refill_hours(settings.weekly_infusions, start_of_week)

        week_hours = create_week_hours(hours_in_a_week)

        level_params = FactorCalculationParameters(
            refill_hours=refill_hours,
            initial_factor_level=settings.initial_factor_level,
            decay_constant=settings.decay_constant,
            week_duration=hours_in_a_week
        )

        levels = calculate_levels(week_hours=week_hours, params=level_params)

        current_time = convert_to_datetime(settings.current_time)
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
        return result
    except Exception as exc:
        raise exc


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


def get_values_for_default_user(db: Session = Depends(get_db)) -> DefaultValues:
    username = "stefanjosan"
    measurement_id = 0

    user = get_user_by_username(db, username)
    measurement = get_user_measurement(db=db, user_id=user.id, measurement_id=measurement_id)
    weekly_infusions = get_refill_times(db, username)
    if measurement:
        decay_constant = calculate_decay_constant(peak_level=measurement.peak_level,
                                                  measured_level=measurement.second_level_measurement,
                                                  time_elapsed=measurement.time_elapsed)
        return DefaultValues(
            decay_constant=decay_constant,
            peak_level=measurement.peak_level,
            time_elapsed=measurement.time_elapsed,
            second_level_measurement=measurement.second_level_measurement,
            weekly_infusions=weekly_infusions
        )


def get_refill_times(db: Session, username: str) -> List[str]:
    user = get_user_by_username(db, username)
    if not user or not user.weekly_infusions:
        return []
    return user.weekly_infusions.split(", ")
