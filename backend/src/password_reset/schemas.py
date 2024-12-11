from pydantic import BaseModel, EmailStr, Field


class PasswordResetRequest(BaseModel):
    identifier: str = Field(
        ...,
        description="Email or username of the user requesting the password reset"
    )


class PasswordResetResponse(BaseModel):
    message: str = Field(..., description="Detail message about the password reset request")


class PasswordReset(BaseModel):
    token: str = Field(
        ...,
        description="Token of the request user"
    )
    new_password: str = Field(
        ...,
        description="New user password"
    )


class PasswordResetResult(BaseModel):
    success: bool = Field(
        ...,
        description="Result of the request link",

    )
    message: str = Field(
        None,
        description="User return message"
    )
