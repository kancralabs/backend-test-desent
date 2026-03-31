"""Centralized error handling middleware for standardized error responses"""
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle Pydantic validation errors (422 Unprocessable Entity).

    Args:
        request: FastAPI request object
        exc: Validation error exception

    Returns:
        JSONResponse with standardized error format
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": str(exc.errors()),
            "status_code": 422,
        },
    )


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """
    Handle database integrity constraint violations (409 Conflict).

    Examples:
    - Unique constraint violations
    - Foreign key violations
    - Check constraint violations

    Args:
        request: FastAPI request object
        exc: Integrity error exception

    Returns:
        JSONResponse with standardized error format
    """
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": "Conflict",
            "detail": "Resource constraint violated",
            "status_code": 409,
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all handler for unhandled exceptions (500 Internal Server Error).

    Logs the exception for debugging but returns generic message to client
    to avoid leaking sensitive information.

    Args:
        request: FastAPI request object
        exc: Exception instance

    Returns:
        JSONResponse with standardized error format
    """
    # TODO: Add proper logging in production
    # logger.exception(f"Unhandled exception: {exc}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred",
            "status_code": 500,
        },
    )
