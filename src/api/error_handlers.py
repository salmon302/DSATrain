"""
Consistent error handling for FastAPI endpoints
Provides standardized error response formats across the API
"""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base API error with consistent structure"""
    
    def __init__(
        self, 
        message: str, 
        code: str = "api_error",
        status_code: int = 500,
        meta: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.meta = meta or {}
        super().__init__(message)


class ValidationAPIError(APIError):
    """Validation error with field-level details"""
    
    def __init__(
        self,
        message: str = "Validation failed",
        errors: Optional[List[str]] = None,
        meta: Optional[Dict[str, Any]] = None
    ):
        self.errors = errors or []
        super().__init__(
            message=message,
            code="validation_error", 
            status_code=400,
            meta=meta
        )


class RateLimitAPIError(APIError):
    """Rate limiting error with retry information"""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after_seconds: Optional[int] = None,
        meta: Optional[Dict[str, Any]] = None
    ):
        self.retry_after_seconds = retry_after_seconds
        super().__init__(
            message=message,
            code="rate_limit_exceeded",
            status_code=429,
            meta=meta
        )


def format_error_response(
    code: str,
    message: str,
    meta: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Format a consistent error response"""
    response = {
        "error": {
            "code": code,
            "message": message
        }
    }
    
    if meta:
        response["meta"] = meta
    
    return response


def format_validation_error_response(
    message: str,
    errors: List[str],
    meta: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Format a validation error response"""
    response = {
        "error": {
            "code": "validation_error",
            "message": message
        },
        "errors": errors
    }
    
    if meta:
        response["meta"] = meta
    
    return response


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """Handle custom API errors"""
    
    logger.warning(f"API Error: {exc.code} - {exc.message}", extra={"meta": exc.meta})
    
    if isinstance(exc, ValidationAPIError):
        content = format_validation_error_response(
            message=exc.message,
            errors=exc.errors,
            meta=exc.meta
        )
    else:
        content = format_error_response(
            code=exc.code,
            message=exc.message,
            meta=exc.meta
        )
    
    headers = {}
    if isinstance(exc, RateLimitAPIError) and exc.retry_after_seconds:
        headers["Retry-After"] = str(exc.retry_after_seconds)
    
    return JSONResponse(
        status_code=exc.status_code,
        content=content,
        headers=headers
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions with consistent format"""
    
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    
    # Handle special cases
    if exc.status_code == 404:
        code = "not_found"
    elif exc.status_code == 403:
        code = "forbidden"
    elif exc.status_code == 401:
        code = "unauthorized"
    elif exc.status_code == 422:
        code = "validation_error"
    elif exc.status_code == 429:
        code = "rate_limit_exceeded"
    else:
        code = "http_error"
    
    # Extract detail if it's already in the expected format
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        content = exc.detail
    else:
        content = format_error_response(
            code=code,
            message=str(exc.detail)
        )
    
    headers = {}
    if hasattr(exc, 'headers') and exc.headers:
        headers.update(exc.headers)
    
    return JSONResponse(
        status_code=exc.status_code,
        content=content,
        headers=headers
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors"""
    
    logger.warning(f"Validation Error: {exc.errors()}")
    
    # Extract field-level errors
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")
    
    content = format_validation_error_response(
        message="Request validation failed",
        errors=errors
    )
    
    return JSONResponse(
        status_code=422,
        content=content
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    
    logger.error(f"Unexpected error: {type(exc).__name__}: {str(exc)}", exc_info=True)
    
    # Don't leak internal errors in production
    content = format_error_response(
        code="internal_error",
        message="An unexpected error occurred"
    )
    
    return JSONResponse(
        status_code=500,
        content=content
    )


def setup_error_handlers(app):
    """Set up error handlers for a FastAPI app"""
    
    app.add_exception_handler(APIError, api_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
