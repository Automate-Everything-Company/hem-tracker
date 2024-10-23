from dataclasses import dataclass
from typing import List, Optional

from pydantic import BaseModel, Field, conlist


class FactorLevelSettings(BaseModel):
    initial_factor_level: float = Field(
        ...,
        alias='peakLevel',
        gt=0,
        description="Initial peak level must be greater than 0."
    )
    decay_constant: float = Field(
        ...,
        alias='decayConstant'
    )
    weekly_infusions: conlist(item_type=str, min_length=1) = Field(
        ...,
        alias='weeklyInfusions',
        description="List of weekly infusion times in ISO 8601 format."
    )
    current_time: str = Field(
        ...,
        alias='currentTime',
        description="Current time in ISO 8601 format."
    )

    class Config:
        populate_by_name = True


class FactorLevels(BaseModel):
    hours: conlist(item_type=float, min_length=1) = Field(
        ...,
        description="Hours of one week in 0.1 interval."
    )
    start_of_week: str = Field(
        ...,
        description="Timestamp of when the week starts (Monday night at 24:00) in ISO 8601 format."
    )
    levels: conlist(item_type=float, min_length=1) = Field(
        ...,
        description="Factor levels in 0.1 interval for the whole week."
    )
    current_time: str = Field(
        ...,
        description="Current time in ISO 8601 format."
    )

    current_factor_level: conlist(item_type=float, min_length=2) = Field(
        ...,
        description="Factor values (time, factor value) now."
    )

    halving_time: float = Field(
        ...,
        description="Factor halving time."
    )

    class Config:
        populate_by_name = True


# class DefaultValues(BaseModel):
#     decay_constant: Optional[float] = Field(None)
#     time_elapsed: Optional[float] = Field(None)
#     second_level_measurement: Optional[float] = Field(None)
#     peak_level: Optional[float] = Field(None)
#     refill_times: Optional[list[str]] = Field(None)


class DefaultValues(BaseModel):
    decay_constant: Optional[float] = Field(
        None,
        title='Decay constant',
        description='Factor level decay constant',
        alias='decayConstant'
    )
    time_elapsed: float = Field(
        ...,
        gt=0,
        title='Elapsed time',
        description='Elapsed time from the last infusion until now'
    )
    second_level_measurement: float = Field(
        ...,
        gt=0,
        title='Second measurement level',
        description='Factor level after the second measurement'
    )
    peak_level: float = Field(
        ...,
        gt=0,
        title='Factor peak',
        description='Factor peak level right after the infusion'
    )
    weekly_infusions: conlist(item_type=str, min_length=1) = Field(
        ...,
        title='Weekly refill times',
        description="List of refill times in ISO 8601 format."
    )

    class Config:
        populate_by_name = True


class DecayConstantParameters(BaseModel):
    peak_level: Optional[float] = Field(..., alias='peakLevel')
    time_elapsed: Optional[float] = Field(..., alias='timeElapsed')
    second_level_measurement: Optional[float] = Field(..., alias='secondLevelMeasurement')

    class Config:
        populate_by_name = True