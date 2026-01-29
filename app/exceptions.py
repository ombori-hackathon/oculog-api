from enum import Enum
from typing import Any

from fastapi import HTTPException


class ErrorType(str, Enum):
    # Auth errors
    INVALID_CREDENTIALS = "invalid_credentials"
    UNAUTHORIZED = "unauthorized"
    EMAIL_ALREADY_EXISTS = "email_already_exists"

    # Resource errors
    NOT_FOUND = "not_found"
    FORBIDDEN = "forbidden"

    # Validation/Conflict errors
    DUPLICATE_DATE = "duplicate_date"
    VALIDATION_ERROR = "validation_error"

    # Server errors
    SERVICE_UNAVAILABLE = "service_unavailable"
    BAD_GATEWAY = "bad_gateway"
    SERVER_ERROR = "server_error"


class AppException(HTTPException):
    """Base exception with unified error format"""

    def __init__(
        self,
        status_code: int,
        error_type: ErrorType,
        message: str,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ):
        self.error_type = error_type
        self.message = message
        self.data = data
        super().__init__(status_code=status_code, detail=message, headers=headers)
