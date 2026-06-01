"""Custom exceptions for API responses."""
from fastapi import HTTPException, status
from typing import Any, Dict, Optional


class APIException(HTTPException):
    """Base API exception."""

    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str = "Internal server error",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class UnauthorizedException(APIException):
    """Raised when authentication fails."""

    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenException(APIException):
    """Raised when user lacks required permissions."""

    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class NotFoundException(APIException):
    """Raised when resource not found."""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class ConflictException(APIException):
    """Raised on resource conflict (e.g., duplicate)."""

    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class ValidationException(APIException):
    """Raised on validation error."""

    def __init__(self, detail: str = "Validation failed"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class RateLimitException(APIException):
    """Raised when rate limit exceeded."""

    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
        )
