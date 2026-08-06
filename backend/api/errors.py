from fastapi import HTTPException


class APIError(Exception):
    def __init__(self, message: str, code: str = "API_ERROR", status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class AuthenticationError(APIError):
    def __init__(self, message: str = "Authentication failed", code: str = "AUTHENTICATION_FAILED", status_code: int = 401):
        super().__init__(message=message, code=code, status_code=status_code)


class ValidationError(APIError):
    def __init__(self, message: str = "Validation failed", code: str = "VALIDATION_ERROR", status_code: int = 422):
        super().__init__(message=message, code=code, status_code=status_code)


class DatabaseError(APIError):
    def __init__(self, message: str = "Database error", code: str = "DATABASE_ERROR", status_code: int = 500):
        super().__init__(message=message, code=code, status_code=status_code)


class InternalServerError(APIError):
    def __init__(self, message: str = "Internal server error", code: str = "INTERNAL_SERVER_ERROR", status_code: int = 500):
        super().__init__(message=message, code=code, status_code=status_code)
