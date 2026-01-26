"""
Standardized API response formats for BarberX Legal Technologies
Ensures consistent client-side handling
"""

from typing import Any, Dict, List, Optional, Union
from flask import jsonify


class APIResponse:
    """Standardized API response builder"""
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "Operation successful",
        status_code: int = 200,
        **kwargs
    ) -> tuple:
        """
        Success response
        
        Args:
            data: Response data (dict, list, or primitive)
            message: Success message
            status_code: HTTP status code (200, 201, etc.)
            **kwargs: Additional fields to include
        
        Returns:
            (response, status_code) tuple for Flask
        """
        response = {
            "success": True,
            "message": message,
            "data": data
        }
        
        # Add any extra fields
        response.update(kwargs)
        
        return jsonify(response), status_code
    
    @staticmethod
    def error(
        message: str = "Operation failed",
        error_code: Optional[str] = None,
        status_code: int = 400,
        details: Optional[Dict] = None,
        error_ticket: Optional[str] = None
    ) -> tuple:
        """
        Error response
        
        Args:
            message: User-friendly error message
            error_code: Machine-readable error code (e.g., 'VALIDATION_ERROR')
            status_code: HTTP status code (400, 401, 403, 404, 500, etc.)
            details: Additional error details (validation errors, etc.)
            error_ticket: Error ticket ID for support
        
        Returns:
            (response, status_code) tuple for Flask
        """
        response = {
            "success": False,
            "message": message
        }
        
        if error_code:
            response["error_code"] = error_code
        
        if details:
            response["details"] = details
        
        if error_ticket:
            response["error_ticket"] = error_ticket
            response["message"] += f" (Support ticket: {error_ticket})"
        
        return jsonify(response), status_code
    
    @staticmethod
    def validation_error(errors: Dict[str, List[str]]) -> tuple:
        """
        Validation error response
        
        Args:
            errors: Dict of field names to error messages
                   e.g., {"email": ["Invalid format"], "password": ["Too short"]}
        
        Returns:
            (response, status_code) tuple for Flask
        """
        return APIResponse.error(
            message="Validation failed",
            error_code="VALIDATION_ERROR",
            status_code=422,
            details={"validation_errors": errors}
        )
    
    @staticmethod
    def unauthorized(message: str = "Authentication required") -> tuple:
        """Unauthorized access response (401)"""
        return APIResponse.error(
            message=message,
            error_code="UNAUTHORIZED",
            status_code=401
        )
    
    @staticmethod
    def forbidden(message: str = "Access denied") -> tuple:
        """Forbidden access response (403)"""
        return APIResponse.error(
            message=message,
            error_code="FORBIDDEN",
            status_code=403
        )
    
    @staticmethod
    def not_found(resource: str = "Resource") -> tuple:
        """Resource not found response (404)"""
        return APIResponse.error(
            message=f"{resource} not found",
            error_code="NOT_FOUND",
            status_code=404
        )
    
    @staticmethod
    def created(data: Any = None, message: str = "Resource created successfully") -> tuple:
        """Resource created response (201)"""
        return APIResponse.success(
            data=data,
            message=message,
            status_code=201
        )
    
    @staticmethod
    def no_content() -> tuple:
        """No content response (204)"""
        return '', 204
    
    @staticmethod
    def paginated(
        items: List,
        page: int,
        per_page: int,
        total: int,
        message: str = "Data retrieved successfully"
    ) -> tuple:
        """
        Paginated response
        
        Args:
            items: List of items for current page
            page: Current page number
            per_page: Items per page
            total: Total number of items
        
        Returns:
            (response, status_code) tuple for Flask
        """
        total_pages = (total + per_page - 1) // per_page
        
        return APIResponse.success(
            data={
                "items": items,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
                }
            },
            message=message
        )
    
    @staticmethod
    def rate_limited(retry_after: Optional[int] = None) -> tuple:
        """
        Rate limit exceeded response (429)
        
        Args:
            retry_after: Seconds until rate limit resets
        
        Returns:
            (response, status_code) tuple for Flask
        """
        message = "Too many requests. Please try again later."
        if retry_after:
            message += f" Retry after {retry_after} seconds."
        
        response = APIResponse.error(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429
        )
        
        if retry_after:
            # Add Retry-After header
            flask_response, status = response
            flask_response.headers['Retry-After'] = str(retry_after)
            return flask_response, status
        
        return response


class ErrorCodes:
    """Standard error codes for client-side handling"""
    
    # Authentication & Authorization
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"
    
    # Validation
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_FIELD = "MISSING_FIELD"
    
    # Resources
    NOT_FOUND = "NOT_FOUND"
    ALREADY_EXISTS = "ALREADY_EXISTS"
    CONFLICT = "CONFLICT"
    
    # Files
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    FILE_TYPE_NOT_ALLOWED = "FILE_TYPE_NOT_ALLOWED"
    FILE_UPLOAD_FAILED = "FILE_UPLOAD_FAILED"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    
    # Operations
    OPERATION_FAILED = "OPERATION_FAILED"
    DATABASE_ERROR = "DATABASE_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    
    # Rate Limiting
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    
    # Tier/Subscription
    TIER_LIMIT_REACHED = "TIER_LIMIT_REACHED"
    FEATURE_NOT_AVAILABLE = "FEATURE_NOT_AVAILABLE"
    UPGRADE_REQUIRED = "UPGRADE_REQUIRED"


# Convenience exports
success_response = APIResponse.success
error_response = APIResponse.error
validation_error = APIResponse.validation_error
created_response = APIResponse.created
paginated_response = APIResponse.paginated
