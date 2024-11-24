from datetime import datetime, timedelta
from typing import List

import numpy as np
import pytz

CET = pytz.timezone('Europe/Berlin')


def convert_to_datetime(date_str):
    now = datetime.now(CET)
    current_year = now.year
    current_month = now.month
    time_part = ' '.join(date_str.split()[1:])  # Gets "10:05 AM"
    datetime_obj = datetime.strptime(time_part, '%I:%M %p')
    datetime_obj = datetime_obj.replace(year=current_year, month=current_month)

    weekday_str = date_str.split()[0]  # Gets "Monday"
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    target_weekday = weekdays.index(weekday_str)
    current_weekday = now.weekday()

    days_difference = target_weekday - current_weekday
    correct_date = now + timedelta(days=days_difference)

    final_datetime = datetime_obj.replace(day=correct_date.day)

    return CET.localize(final_datetime)


def generate_refill_hours(refill_times: List[str], start_of_week: datetime) -> List[float]:
    refill_times_in_datetime_format = generate_refill_times_in_datetime_format(refill_times, start_of_week)
    refill_hours = generate_refill_times_in_hour_format(refill_times_in_datetime_format, start_of_week)
    return refill_hours


def generate_refill_times_in_datetime_format(refill_times, start_of_week):
    refill_datetimes = []

    for time_str in refill_times:
        refill_time_in_datetime = parse_refill_time(time_str, start_of_week)
        refill_datetimes.append(refill_time_in_datetime)

    return refill_datetimes


def parse_refill_time(time_str: str, start_of_week: datetime) -> datetime:
    now = datetime.now(CET)
    current_year = now.year
    current_month = now.month
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_part, *time_part = time_str.split()
    day_of_week = weekdays.index(day_part)
    time_part = " ".join(time_part)
    time_obj = datetime.strptime(time_part, "%I:%M %p")
    time_obj = time_obj.replace(year=current_year, month=current_month)
    day_datetime = start_of_week + timedelta(days=day_of_week)
    return day_datetime.replace(hour=time_obj.hour, minute=time_obj.minute)


def generate_refill_times_in_hour_format(refill_times_in_datetime_format, start_of_week):
    refill_hours_in_numbers = []
    for refill_time_in_datetime in refill_times_in_datetime_format:
        refill_time_in_hour = float(
            f"{(refill_time_in_datetime - start_of_week).total_seconds() / 3600:.1f}")  # one decimal float
        refill_hours_in_numbers.append(refill_time_in_hour)
    return refill_hours_in_numbers


def get_start_of_the_week():
    start_of_week = CET.localize(
        datetime.combine(datetime.now(CET).date() - timedelta(days=datetime.now(CET).date().weekday()),
                         datetime.min.time()))
    return start_of_week


def create_week_hours(hours_in_a_week):
    week_hours = np.arange(0, hours_in_a_week, 0.1).round(2)
    week_hours = week_hours.tolist()
    return week_hours

