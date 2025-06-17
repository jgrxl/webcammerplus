import logging
import traceback
from functools import wraps
from typing import Any, Callable, Dict, Optional

from flask import current_app, request
from werkzeug.exceptions import HTTPException

from common.response_models import error_response

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base application error class."""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        status_code: int = 400,
        details: Optional[Any] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details


class ValidationError(AppError):
    """Validation error."""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message, "VALIDATION_ERROR", 400, details)


class AuthenticationError(AppError):
    """Authentication error."""

    def __init__(
        self, message: str = "Authentication required", details: Optional[Any] = None
    ):
        super().__init__(message, "AUTH_REQUIRED", 401, details)


class AuthorizationError(AppError):
    """Authorization error."""

    def __init__(
        self, message: str = "Insufficient permissions", details: Optional[Any] = None
    ):
        super().__init__(message, "FORBIDDEN", 403, details)


class NotFoundError(AppError):
    """Resource not found error."""

    def __init__(
        self, message: str = "Resource not found", details: Optional[Any] = None
    ):
        super().__init__(message, "NOT_FOUND", 404, details)


class RateLimitError(AppError):
    """Rate limit exceeded error."""

    def __init__(
        self, message: str = "Rate limit exceeded", details: Optional[Any] = None
    ):
        super().__init__(message, "RATE_LIMIT_EXCEEDED", 429, details)


class ExternalServiceError(AppError):
    """External service error."""

    def __init__(self, service: str, message: str, details: Optional[Any] = None):
        super().__init__(
            f"{service} service error: {message}",
            "EXTERNAL_SERVICE_ERROR",
            503,
            {"service": service, **(details or {})},
        )


def handle_app_error(error: AppError) -> tuple[Dict[str, Any], int]:
    """Handle application errors.

    Args:
        error: AppError instance

    Returns:
        Error response tuple
    """
    logger.error(
        f"Application error: {error.message}",
        extra={
            "error_code": error.code,
            "status_code": error.status_code,
            "details": error.details,
            "path": request.path if request else None,
            "method": request.method if request else None,
        },
    )

    return error_response(
        error=error.message,
        code=error.code,
        details=error.details,
        status_code=error.status_code,
    )


def handle_http_exception(error: HTTPException) -> tuple[Dict[str, Any], int]:
    """Handle Werkzeug HTTP exceptions.

    Args:
        error: HTTPException instance

    Returns:
        Error response tuple
    """
    return error_response(
        error=error.description or str(error),
        code=error.name.upper().replace(" ", "_"),
        status_code=error.code or 500,
    )


def handle_generic_exception(error: Exception) -> tuple[Dict[str, Any], int]:
    """Handle generic exceptions.

    Args:
        error: Exception instance

    Returns:
        Error response tuple
    """
    logger.exception(
        "Unhandled exception",
        extra={
            "path": request.path if request else None,
            "method": request.method if request else None,
        },
    )

    # In production, hide internal error details
    if current_app.config.get("ENV") == "production":
        return error_response(
            error="An internal error occurred", code="INTERNAL_ERROR", status_code=500
        )
    else:
        return error_response(
            error=str(error),
            code="INTERNAL_ERROR",
            details={"traceback": traceback.format_exc()},
            status_code=500,
        )


def register_error_handlers(app):
    """Register error handlers with Flask app.

    Args:
        app: Flask application instance
    """

    @app.errorhandler(AppError)
    def handle_app_errors(error):
        return handle_app_error(error)

    @app.errorhandler(HTTPException)
    def handle_http_errors(error):
        return handle_http_exception(error)

    @app.errorhandler(Exception)
    def handle_all_errors(error):
        return handle_generic_exception(error)


def error_handler(f: Callable) -> Callable:
    """Decorator for handling errors in route handlers.

    Args:
        f: Function to decorate

    Returns:
        Decorated function
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except AppError as e:
            return handle_app_error(e)
        except HTTPException as e:
            return handle_http_exception(e)
        except Exception as e:
            return handle_generic_exception(e)

    return decorated


def validate_request(schema: Dict[str, Any]) -> Callable:
    """Decorator for validating request data.

    Args:
        schema: Validation schema

    Returns:
        Decorator function
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            # Simple validation example - can be extended with marshmallow/pydantic
            data = request.get_json() if request.is_json else {}

            for field, rules in schema.items():
                if rules.get("required") and field not in data:
                    raise ValidationError(f"Missing required field: {field}")

                if field in data and "type" in rules:
                    expected_type = rules["type"]
                    if not isinstance(data[field], expected_type):
                        raise ValidationError(
                            f"Invalid type for field {field}: expected {expected_type.__name__}"
                        )

            return f(*args, **kwargs)

        return decorated

    return decorator
