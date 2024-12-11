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
        populate_by_name = True