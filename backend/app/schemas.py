from datetime import datetime

from pydantic import BaseModel, Field
from typing import Optional, List


class DefaultValues(BaseModel):
    decay_constant: Optional[float] = Field(None)
    time_elapsed: Optional[float] = Field(None)
    second_level_measurement: Optional[float] = Field(None)
    peak_level: Optional[float] = Field(None)
    refill_times: Optional[list[str]] = Field(None)


class UserSignup(BaseModel):
    first_name: Optional[str] = Field(None, alias='firstName')
    last_name: Optional[str] = Field(None, alias='lastName')
    username: str
    password: str
    email: Optional[str] = None
    peak_level: float
    weekly_infusions: Optional[List[str]] = None

    class Config:
        populate_by_name = True


class UserBase(BaseModel):
    first_name: str = None
    last_name: str = None
    username: str
    email: Optional[str] = None
    peak_level: float
    weekly_infusions: Optional[str] = None


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    class Config:
        from_attributes = True


class UserPlotsData(BaseModel):
    decay_constant: float = Field(..., alias='decayConstant')
    peak_level: float = Field(..., alias='peakLevel')
    refill_times: List[str] = Field(..., alias='refillTimes')
    current_level: str = Field(..., alias='currentTime')

    class Config:
        populate_by_name = True
        from_attributes = True


class MeasurementBase(BaseModel):
    peak_level: Optional[float] = None
    time_elapsed: Optional[float] = None
    second_level_measurement: Optional[float] = None
    halving_time: Optional[float] = None
    decay_constant: Optional[float] = None
    comment: Optional[str] = None


class MeasurementCreate(MeasurementBase):
    peak_level: Optional[float] = None
    time_elapsed: Optional[float] = None
    second_level_measurement: Optional[float] = None
    halving_time: Optional[float] = None
    decay_constant: Optional[float] = None
    comment: Optional[str] = None


class Measurement(MeasurementBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class DecayConstantParameters(BaseModel):
    peak_level: Optional[float] = Field(..., alias='peakLevel')
    time_elapsed: Optional[float] = Field(..., alias='timeElapsed')
    second_level_measurement: Optional[float] = Field(..., alias='secondLevelMeasurement')

    class Config:
        populate_by_name = True


class UserUpdate(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    peak_level: Optional[float] = None
    weekly_infusions: Optional[List[str]] = None


class Token(BaseModel):
    access_token: str
    token_type: str


class ContactForm(BaseModel):
    email: Optional[str] = None
    message: Optional[str] = None


class PasswordResetRequest(BaseModel):
    identifier: Optional[str] = None


class PasswordReset(BaseModel):
    token: str
    new_password: str
