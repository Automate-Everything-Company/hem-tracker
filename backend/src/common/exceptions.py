from fastapi import HTTPException, status


class UserAlreadyExistsError(HTTPException):
    def __init__(self, detail: str = "Username of email already exist"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class DatabaseError(HTTPException):
    def __init__(self, detail: str = "Could not register user"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class EmailSendingFailedException(HTTPException):
    def __init__(self, detail: str = "Failed to send password reset email. Please contact support."):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class UserNotFoundException(HTTPException):
    def __init__(self, detail: str = "If your email or username is registered, you will receive reset instructions."):
        super().__init__(status_code=status.HTTP_200_OK, detail=detail)


class InvalidTokenException(HTTPException):
    def __init__(self, detail: str = "Invalid or expired token"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
