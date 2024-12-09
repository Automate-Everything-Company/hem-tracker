from typing import Literal

from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str = Field(
        ...,
        description="JWT access token",
    )

    token_type: Literal["bearer"] = Field(
        ...,
        description="Type of token",
    )

    expires_in: int = Field(..., description="Token expiration time in seconds", gt=0)

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
            }
        }
