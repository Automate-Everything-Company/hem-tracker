from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str = Field(
        ...,
        description="JWT access token",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkw..."
    )

    token_type: str = Field(
        ...,
        description="Type of token",
        example="bearer"
    )

    expires_in: int = Field(
        ...,
        description="Token expiration time in seconds",
        example=3600,
        gt=0
    )

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
            }
        }
