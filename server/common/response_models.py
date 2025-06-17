from typing import Any, Dict, Optional

from flask_restx import Model, fields


def create_error_model(api) -> Model:
    """Create a standardized error response model.

    Args:
        api: Flask-RESTx API instance

    Returns:
        Error response model
    """
    return api.model(
        "ErrorResponse",
        {
            "error": fields.String(required=True, description="Error message"),
            "code": fields.String(description="Error code", example="AUTH_REQUIRED"),
            "details": fields.Raw(description="Additional error details"),
            "request_id": fields.String(description="Request tracking ID"),
        },
    )


def create_success_model(api, name: str, data_fields: Dict[str, Any]) -> Model:
    """Create a standardized success response model.

    Args:
        api: Flask-RESTx API instance
        name: Model name
        data_fields: Fields for the data payload

    Returns:
        Success response model
    """
    return api.model(
        name,
        {
            "success": fields.Boolean(default=True, description="Operation status"),
            "data": fields.Nested(
                api.model(f"{name}Data", data_fields), description="Response data"
            ),
            "metadata": fields.Raw(description="Additional metadata"),
        },
    )


def create_pagination_model(api) -> Model:
    """Create pagination metadata model.

    Args:
        api: Flask-RESTx API instance

    Returns:
        Pagination model
    """
    return api.model(
        "Pagination",
        {
            "page": fields.Integer(description="Current page number", min=1),
            "per_page": fields.Integer(description="Items per page", min=1, max=100),
            "total": fields.Integer(description="Total number of items"),
            "pages": fields.Integer(description="Total number of pages"),
            "has_prev": fields.Boolean(description="Has previous page"),
            "has_next": fields.Boolean(description="Has next page"),
        },
    )


def create_usage_stats_model(api) -> Model:
    """Create usage statistics model.

    Args:
        api: Flask-RESTx API instance

    Returns:
        Usage stats model
    """
    return api.model(
        "UsageStats",
        {
            "subscription_tier": fields.String(description="Current subscription tier"),
            "usage_reset_date": fields.DateTime(description="When usage resets"),
            "current_usage": fields.Raw(description="Current usage by operation"),
            "limits": fields.Raw(description="Tier limits"),
            "usage_percentage": fields.Raw(description="Usage as percentage of limits"),
        },
    )


def create_subscription_model(api) -> Model:
    """Create subscription information model.

    Args:
        api: Flask-RESTx API instance

    Returns:
        Subscription model
    """
    return api.model(
        "Subscription",
        {
            "tier": fields.String(
                description="Subscription tier", enum=["free", "pro", "max"]
            ),
            "status": fields.String(
                description="Subscription status",
                enum=["active", "inactive", "cancelled", "past_due"],
            ),
            "start_date": fields.DateTime(description="Subscription start date"),
            "end_date": fields.DateTime(description="Subscription end date"),
            "stripe_customer_id": fields.String(description="Stripe customer ID"),
        },
    )


def create_user_model(api) -> Model:
    """Create user information model.

    Args:
        api: Flask-RESTx API instance

    Returns:
        User model
    """
    return api.model(
        "User",
        {
            "id": fields.String(description="User ID (Auth0 sub)"),
            "email": fields.String(description="User email"),
            "name": fields.String(description="User name"),
            "picture": fields.String(description="Profile picture URL"),
            "email_verified": fields.Boolean(description="Email verified status"),
            "subscription": fields.Nested(
                create_subscription_model(api), description="Subscription information"
            ),
            "created_at": fields.DateTime(description="Account creation date"),
            "last_login": fields.DateTime(description="Last login date"),
        },
    )


# Standard response helpers
def success_response(
    data: Any = None,
    message: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Create a standardized success response.

    Args:
        data: Response data
        message: Optional success message
        metadata: Optional metadata

    Returns:
        Success response dictionary
    """
    response = {"success": True}

    if data is not None:
        response["data"] = data

    if message:
        response["message"] = message

    if metadata:
        response["metadata"] = metadata

    return response


def error_response(
    error: str,
    code: Optional[str] = None,
    details: Optional[Any] = None,
    status_code: int = 400,
) -> tuple[Dict[str, Any], int]:
    """Create a standardized error response.

    Args:
        error: Error message
        code: Optional error code
        details: Optional error details
        status_code: HTTP status code

    Returns:
        Tuple of (error response dictionary, status code)
    """
    response = {"error": error}

    if code:
        response["code"] = code

    if details:
        response["details"] = details

    return response, status_code


# Common field definitions for reuse
COMMON_FIELDS = {
    "id": fields.String(description="Resource ID"),
    "created_at": fields.DateTime(description="Creation timestamp"),
    "updated_at": fields.DateTime(description="Last update timestamp"),
    "email": fields.String(description="Email address"),
    "url": fields.String(description="Resource URL"),
}


# Request parsers
def create_pagination_parser():
    """Create pagination request parser.

    Returns:
        Request parser for pagination parameters
    """
    from flask_restx import reqparse

    parser = reqparse.RequestParser()
    parser.add_argument("page", type=int, default=1, help="Page number (default: 1)")
    parser.add_argument(
        "per_page", type=int, default=20, help="Items per page (default: 20, max: 100)"
    )
    parser.add_argument("sort", type=str, help="Sort field")
    parser.add_argument(
        "order", type=str, choices=["asc", "desc"], default="desc", help="Sort order"
    )
    return parser
