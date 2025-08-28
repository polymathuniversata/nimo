"""
Comprehensive error handling utilities for Nimo Platform.
Provides consistent error responses, exception tracking, and recovery mechanisms.
"""

import logging
import traceback
import time
from functools import wraps
from typing import Dict, Any, Optional, Callable, Type, Union
from flask import jsonify, request, current_app, g
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)

class NimoException(Exception):
    """Base exception for Nimo-specific errors"""
    
    def __init__(
        self, 
        message: str, 
        error_code: str = None,
        status_code: int = 500,
        details: Dict[str, Any] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.status_code = status_code
        self.details = details or {}
        self.timestamp = time.time()

class ValidationError(NimoException):
    """Validation error"""
    def __init__(self, message: str, field: str = None, **kwargs):
        super().__init__(message, status_code=400, **kwargs)
        if field:
            self.details['field'] = field

class AuthenticationError(NimoException):
    """Authentication error"""
    def __init__(self, message: str = "Authentication required", **kwargs):
        super().__init__(message, status_code=401, **kwargs)

class AuthorizationError(NimoException):
    """Authorization error"""
    def __init__(self, message: str = "Access denied", **kwargs):
        super().__init__(message, status_code=403, **kwargs)

class NotFoundError(NimoException):
    """Resource not found error"""
    def __init__(self, resource: str = "Resource", resource_id: str = None, **kwargs):
        message = f"{resource} not found"
        if resource_id:
            message += f": {resource_id}"
        super().__init__(message, status_code=404, **kwargs)
        if resource_id:
            self.details['resource_id'] = resource_id

class ConflictError(NimoException):
    """Resource conflict error"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, status_code=409, **kwargs)

class RateLimitError(NimoException):
    """Rate limit exceeded error"""
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None, **kwargs):
        super().__init__(message, status_code=429, **kwargs)
        if retry_after:
            self.details['retry_after'] = retry_after

class ExternalServiceError(NimoException):
    """External service error"""
    def __init__(self, service: str, message: str = None, **kwargs):
        message = message or f"{service} service unavailable"
        super().__init__(message, status_code=503, **kwargs)
        self.details['service'] = service

class MeTTaServiceError(ExternalServiceError):
    """MeTTa service specific error"""
    def __init__(self, message: str = "MeTTa service error", **kwargs):
        super().__init__("MeTTa", message, **kwargs)

class BlockchainError(ExternalServiceError):
    """Blockchain service error"""
    def __init__(self, message: str = "Blockchain service error", **kwargs):
        super().__init__("Blockchain", message, **kwargs)

class DatabaseError(NimoException):
    """Database operation error"""
    def __init__(self, message: str = "Database operation failed", **kwargs):
        super().__init__(message, status_code=500, **kwargs)

class ErrorHandler:
    """Centralized error handling class"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize error handlers for Flask app"""
        app.register_error_handler(NimoException, self.handle_nimo_exception)
        app.register_error_handler(HTTPException, self.handle_http_exception)
        app.register_error_handler(Exception, self.handle_generic_exception)
    
    def handle_nimo_exception(self, error: NimoException):
        """Handle custom Nimo exceptions"""
        logger.warning(
            f"Nimo exception: {error.error_code} - {error.message}",
            extra={
                'error_code': error.error_code,
                'status_code': error.status_code,
                'details': error.details,
                'timestamp': error.timestamp
            }
        )
        
        response_data = {
            'success': False,
            'error': error.error_code,
            'message': error.message,
            'timestamp': error.timestamp
        }
        
        if error.details:
            response_data['details'] = error.details
        
        # Add debug information in development
        if current_app.debug:
            response_data['debug'] = {
                'exception_type': error.__class__.__name__,
                'traceback': traceback.format_exc()
            }
        
        return jsonify(response_data), error.status_code
    
    def handle_http_exception(self, error: HTTPException):
        """Handle HTTP exceptions"""
        logger.warning(f"HTTP exception: {error.code} - {error.description}")
        
        response_data = {
            'success': False,
            'error': error.name,
            'message': error.description,
            'timestamp': time.time()
        }
        
        return jsonify(response_data), error.code
    
    def handle_generic_exception(self, error: Exception):
        """Handle unexpected exceptions"""
        error_id = f"error_{int(time.time())}_{id(error)}"
        
        logger.error(
            f"Unexpected error [{error_id}]: {str(error)}",
            exc_info=error,
            extra={
                'error_id': error_id,
                'error_type': error.__class__.__name__
            }
        )
        
        response_data = {
            'success': False,
            'error': 'InternalServerError',
            'message': 'An unexpected error occurred',
            'error_id': error_id,
            'timestamp': time.time()
        }
        
        # Add debug information in development
        if current_app.debug:
            response_data['debug'] = {
                'exception_type': error.__class__.__name__,
                'exception_message': str(error),
                'traceback': traceback.format_exc()
            }
        
        return jsonify(response_data), 500

def handle_errors(
    exceptions: Union[Type[Exception], tuple] = Exception,
    default_message: str = "Operation failed",
    default_status: int = 500,
    log_level: int = logging.ERROR
):
    """
    Decorator for comprehensive error handling.
    
    Args:
        exceptions: Exception types to handle
        default_message: Default error message
        default_status: Default HTTP status code
        log_level: Logging level for caught exceptions
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except NimoException:
                # Re-raise custom exceptions to be handled by error handler
                raise
            except exceptions as e:
                # Log the error
                logger.log(
                    log_level,
                    f"Error in {func.__name__}: {str(e)}",
                    exc_info=e
                )
                
                # Convert to appropriate custom exception
                if isinstance(e, ValueError):
                    raise ValidationError(str(e))
                elif isinstance(e, PermissionError):
                    raise AuthorizationError(str(e))
                elif isinstance(e, FileNotFoundError):
                    raise NotFoundError("File", str(e))
                else:
                    raise NimoException(
                        default_message,
                        status_code=default_status,
                        details={'original_error': str(e)}
                    )
        
        return wrapper
    return decorator

def validate_required_fields(data: Dict[str, Any], required_fields: list):
    """
    Validate that required fields are present in data.
    
    Args:
        data: Data dictionary to validate
        required_fields: List of required field names
        
    Raises:
        ValidationError: If any required field is missing
    """
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    
    if missing_fields:
        raise ValidationError(
            f"Missing required fields: {', '.join(missing_fields)}",
            details={'missing_fields': missing_fields}
        )

def validate_field_types(data: Dict[str, Any], field_types: Dict[str, type]):
    """
    Validate field types in data.
    
    Args:
        data: Data dictionary to validate
        field_types: Dictionary mapping field names to expected types
        
    Raises:
        ValidationError: If any field has wrong type
    """
    for field, expected_type in field_types.items():
        if field in data and data[field] is not None:
            if not isinstance(data[field], expected_type):
                raise ValidationError(
                    f"Field '{field}' must be of type {expected_type.__name__}",
                    field=field,
                    details={
                        'field': field,
                        'expected_type': expected_type.__name__,
                        'actual_type': type(data[field]).__name__
                    }
                )

def safe_execute(
    func: Callable,
    default_return=None,
    log_errors: bool = True,
    raise_on_error: bool = False
) -> Any:
    """
    Safely execute a function with error handling.
    
    Args:
        func: Function to execute
        default_return: Value to return on error
        log_errors: Whether to log errors
        raise_on_error: Whether to re-raise exceptions
        
    Returns:
        Function result or default_return on error
    """
    try:
        return func()
    except Exception as e:
        if log_errors:
            logger.error(f"Safe execution failed for {func.__name__}: {str(e)}", exc_info=e)
        
        if raise_on_error:
            raise
        
        return default_return

class RetryHandler:
    """Handler for retry logic with exponential backoff"""
    
    @staticmethod
    def with_retry(
        max_retries: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        exceptions: tuple = (Exception,)
    ):
        """
        Decorator for retrying failed operations.
        
        Args:
            max_retries: Maximum number of retry attempts
            delay: Initial delay between retries
            backoff: Backoff multiplier for delay
            exceptions: Exception types to retry on
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                current_delay = delay
                last_exception = None
                
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        
                        if attempt < max_retries:
                            logger.warning(
                                f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. "
                                f"Retrying in {current_delay}s..."
                            )
                            time.sleep(current_delay)
                            current_delay *= backoff
                        else:
                            logger.error(
                                f"All {max_retries + 1} attempts failed for {func.__name__}: {str(e)}"
                            )
                
                # If we get here, all retries failed
                raise last_exception
            
            return wrapper
        return decorator

class CircuitBreaker:
    """Circuit breaker pattern for external service calls"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open
    
    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == 'open':
            if time.time() - self.last_failure_time < self.timeout:
                raise ExternalServiceError(
                    func.__name__,
                    f"Circuit breaker is open for {func.__name__}"
                )
            else:
                self.state = 'half-open'
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = 'closed'
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'open'
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")

# Global instances
error_handler = ErrorHandler()
default_circuit_breaker = CircuitBreaker()

def init_error_handling(app):
    """Initialize error handling for Flask app"""
    error_handler.init_app(app)
    
    # Add request context for error tracking
    @app.before_request
    def add_request_context():
        g.request_start_time = time.time()
    
    @app.after_request
    def log_request_duration(response):
        if hasattr(g, 'request_start_time'):
            duration = time.time() - g.request_start_time
            if duration > 5.0:  # Log slow requests
                logger.warning(
                    f"Slow request: {request.method} {request.path} took {duration:.2f}s",
                    extra={
                        'duration': duration,
                        'method': request.method,
                        'path': request.path,
                        'status_code': response.status_code
                    }
                )
        return response