from pydantic import BaseModel, Field, EmailStr, constr, conlist
from typing import Optional, List

from backend.src.measurement.schemas import MeasurementResponse


class UserBase(BaseModel):
    username: constr(max_length=255) = Field(
        ..., description="Username for the user"
    )
    first_name: Optional[constr(max_length=255)] = Field(
        None, description="User's first name"
    )
    last_name: Optional[constr(max_length=255)] = Field(
        None, description="User's last name"
    )
    email: Optional[EmailStr] = Field(
        None, description="User's email address"
    )
    weekly_infusions: str = Field(
        None,
        description="List of weekly infusion times. Do not expect to exceed 5, a maximum of 20 defined."
    )
    peak_level: float = Field(..., description="Peak factor level")

    class Config:
        from_attribute = True


class UserDataResponse(UserBase):
    weekly_infusions: str = Field(
        None,
        description="List of weekly infusion times. Do not expect to exceed 5, a maximum of 20 defined."
    )
    measurements: conlist(MeasurementResponse, min_length=1, max_length=100) = Field(
        default_factory=list,
        description="List of user measurements"
    )

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    password: constr(min_length=1, max_length=255) = Field(
        ..., description="User's password (must be provided during creation)"
    )


class UserRead(UserBase):
    id: int = Field(
        ..., description="User's unique identifier"
    )
    measurements: Optional[List] = Field(
        [], description="List of measurements for the user"
    )


class UserUpdate(UserBase):
    username: str = Field(..., description="Username", max_length=255)  # Required
    first_name: Optional[constr(max_length=255, min_length=0)] = Field(
        None, description="User's first name"
    )
    last_name: Optional[constr(max_length=255, min_length=0)] = Field(
        None, description="User's last name"
    )

    email: Optional[EmailStr] = None
    weekly_infusions: Optional[str] = None
    peak_level: Optional[float] = Field(None, description="Peak factor level")


class UserDelete(UserBase):
    username: str = Field(
        ...,
        description="Username"
    )

    class Config:
        from_attributes = True


class UserPlotData(UserBase):
    username: str = Field(..., alias='username', description='Username')
    decay_constant: float = Field(..., alias="decayConstant", description="Factor decay constant")
    peak_level: float = Field(..., alias="peakLevel", description="Peak factor level")
    weekly_infusions: conlist(str, min_length=1, max_length=20) = Field(
        ...,
        alias="weeklyInfusions",
        description="List of weekly infusion times. Do not expect to exceed 5, a maximum of 20 defined."
    )

    class Config:
        populate_by_name = True
        from_attributes = True


class UserResponse(BaseModel):
    success: bool = Field(
        None,
        description="Result of the request link",

    )
    message: str = Field(
        None,
        description="User return message"
    )


class UserSignup(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=1)
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    peak_level: float = Field(..., gt=0)
    weekly_infusions: conlist(str, min_length=1, max_length=20) = Field(
        ...,
        description="List of weekly infusion times. Do not expect to exceed 5, a maximum of 20 defined."
    )


class SignupResponse(BaseModel):
    detail: str = Field(..., example="Signup successful")
