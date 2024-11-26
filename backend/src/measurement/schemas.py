from typing import Optional

from pydantic import BaseModel, Field


#  todo: rewrite the schemas after this model:
#
# class MeasurementBase(BaseModel):
#     """Base class with common fields for all measurement operations"""
#     peak_level: float = Field(..., description="Peak factor level")
#     time_elapsed: float = Field(..., description="Elapsed time until second measurement")
#     second_level_measurement: float = Field(..., description="Factor level after second measurement")
#     decay_constant: float = Field(..., description="Factor decay constant")
#     halving_time: float = Field(..., description="Factor halving time")
#     comment: Optional[str] = Field(None, description="User comment")
#
#     class Config:
#         from_attributes = True
#
#
# class MeasurementCreate(MeasurementBase):
#     """Schema for creating a new measurement (no ID needed)"""
#     user_id: int = Field(..., description="User id for the measurement")
#
#
# class MeasurementRead(MeasurementBase):
#     """Schema for reading measurement data (includes ID)"""
#     id: int = Field(..., description="Measurement id")
#     user_id: int = Field(..., description="User id for the measurement")
#
#
# class MeasurementUpdate(BaseModel):
#     """Schema for updating an existing measurement (all fields optional)"""
#     peak_level: Optional[float] = Field(None, description="Peak factor level")
#     time_elapsed: Optional[float] = Field(None, description="Elapsed time until second measurement")
#     second_level_measurement: Optional[float] = Field(None, description="Factor level after second measurement")
#     decay_constant: Optional[float] = Field(None, description="Factor decay constant")
#     halving_time: Optional[float] = Field(None, description="Factor halving time")
#     comment: Optional[str] = Field(None, description="User comment")
#
#     class Config:
#         from_attributes = True
#  todo: until here
class MeasurementBase(BaseModel):
    peak_level: float = Field(..., description="Peak factor level")
    time_elapsed: float = Field(..., description="Elapsed time until second measurement")
    second_level_measurement: float = Field(..., description="Factor level after second measurement")
    decay_constant: float = Field(..., description="Factor decay constant")
    halving_time: float = Field(..., description="Factor halving time")
    comment: Optional[str] = Field(None, description="User comment")

    class Config:
        from_attributes = True


class MeasurementCreate(BaseModel):
    user_id: int = Field(..., description="User id for the measurement")
    peak_level: float = Field(..., description="Peak factor level")
    time_elapsed: float = Field(..., description="Elapsed time until second measurement")
    second_level_measurement: float = Field(..., description="Factor level after second measurement")
    decay_constant: float = Field(..., description="Factor decay constant")
    halving_time: float = Field(..., description="Factor halving time")
    comment: Optional[str] = Field(None, description="User comment")


class MeasurementDelete(BaseModel):
    id: int = Field(..., description="Measurement id")
    user_id: int = Field(..., description="User id for the measurement")


class MeasurementRequest(BaseModel):
    peak_level: float = Field(..., description="Peak factor level")
    time_elapsed: float = Field(..., description="Elapsed time until second measurement")
    second_level_measurement: float = Field(..., description="Factor level after second measurement")
    comment: Optional[str] = Field(None, description="User comment")


class UserMeasurements(MeasurementBase):
    id: int = Field(..., description="Measurement id")
    peak_level: float = Field(..., description="Peak factor level")
    time_elapsed: float = Field(..., description="Elapsed time until second measurement")
    second_level_measurement: float = Field(..., description="Factor level after second measurement")
    halving_time: float = Field(..., description="Factor halving time")
    comment: Optional[str] = Field(None, description="User comment")


class Measurement(MeasurementBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class MeasurementResponse(BaseModel):
    id: int = Field(..., description="Measurement ID")
    user_id: int = Field(..., description="User id")
    peak_level: float = Field(..., description="Peak factor level")
    time_elapsed: float = Field(..., description="Elapsed time until second measurement")
    second_level_measurement: float = Field(..., description="Factor level after second measurement")
    decay_constant: float = Field(..., description="Factor decay constant")
    halving_time: float = Field(..., description="Factor halving time")
    comment: Optional[str] = Field(None, description="User comment")

    class Config:
        from_attributes = True
