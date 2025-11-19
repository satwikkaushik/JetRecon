"""Custom error classes and handlers"""

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request
from typing import Any, Dict


def custom_validation_error_handler(request: Request, exc: RequestValidationError):
    """Custom handler for Pydantic Validation errors."""

    return JSONResponse(
        status_code=422,
        content={
            "message": "Validation Error",
            "details": f"Invalid request body or parameters. {exc.errors()}",
        },
    )


class AppError(Exception):
    """
    Base class for all custom errors in the application
    Used to ensure consistent exception handling
    """

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        details: Dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "details": self.details,
        }


class InvalidInputError(AppError):
    def __init__(self, message="Invalid input", details=None):
        super().__init__(message, 422, details)


class NotFoundError(AppError):
    def __init__(self, message="Resource not found", details=None):
        super().__init__(message, 404, details)


class ConflictError(AppError):
    def __init__(self, message="Conflict", details=None):
        super().__init__(message, 409, details)


class ProcessingError(AppError):
    def __init__(self, message="Error during processing", details=None):
        super().__init__(message, 500, details)
