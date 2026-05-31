# app/core/exceptions.py

import traceback
import logging

from fastapi import FastAPI, Request, status
from typing import Any, Optional

from fastapi.responses import JSONResponse
from pydantic import BaseModel


logger = logging.getLogger(__name__)



class ErrorResponse(BaseModel):
    """ Standard error response schema. """

    error: str
    message: str
    details: Optional[dict[str, Any]] = None
    request_id: Optional[str] = None

class AppException(Exception):
    """
    Base exception for application errors.
    All custom exceptions should inherit from this.
    """

    def __init__(
            self,
            message: str,
            error_code: str = "INTERNAL_ERROR",
            status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
            details: Optional[dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details
        super().__init__(message)

class NotFoundError(AppException):
    """ Raised when a requested resource is not found. """

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} with id '{identifier}' not found.",
            error_code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource, "identifier": identifier},
        )

class RequestValidationError(AppException):
    """ Raised when request validation fails. """

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            details=details,
        )

class AuthenticationError(AppException):
    """ Raised when authentication fails. """

    def __init__(self, message="Authentication required"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_FAILED",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

class AuthorizationError(AppException):
    """ Raised when user lacks required permissions. """

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_FAILED",
            status_code=status.HTTP_403_FORBIDDEN,
        )

def setup_exception_handlers(app: FastAPI):
    """
    Register exception handlers with FastAPI.
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(
            request: Request, exc: AppException
    ) -> JSONResponse:
        """ Handle custom application exceptions. """

        # Get request ID from headers if present
        request_id = request.headers.get("X-Request-ID")

        # Log the error
        logger.error(
            f"AppException: {exc.error_code} - {exc.message}",
            extra={
                "request_id": request_id,
                "status_code": exc.status_code,
                "details": exc.details,
            },
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=exc.error_code,
                message=exc.message,
                details=exc.details,
                request_id=request_id,
            ).model_dump(),
        )
    
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
            request: Request, exc: Exception
    ) -> JSONResponse:
        """
        Catch-all handler for unhandled exceptions.
        In production, hide internal details from clients.
        """

        # Get request ID from headers if present
        request_id = request.headers.get("X-Request-ID")

        # Log full traceback for debugging
        logger.error(
            f"Unhandled exception: {str(exc)}",
            extra={
                "request_id": request_id,
                "traceback": traceback.format_exc(),
            },
        )

        # Return generic error to client
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="INTERNAL_ERROR",
                message="An unexpected error occured",
                request_id=request_id,
            ).model_dump(),
        )