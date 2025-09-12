"""
Unified Error Handling for Nimo Platform

This module provides centralized error handling and standardized error responses
for all blockchain services and API endpoints.
"""

import logging
from typing import Dict, Any, Optional, Union
from flask import jsonify
from dataclasses import dataclass
from enum import Enum

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories for better classification"""
    NETWORK = "network"
    BLOCKCHAIN = "blockchain"
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    CONFIGURATION = "configuration"
    SERVICE = "service"
    DATABASE = "database"
    EXTERNAL_API = "external_api"
    UNKNOWN = "unknown"

@dataclass
class NimoError:
    """Standardized error structure"""
    code: str
    message: str
    category: ErrorCategory
    severity: ErrorSeverity
    details: Optional[Dict[str, Any]] = None
    service: Optional[str] = None
    operation: Optional[str] = None
    recoverable: bool = True

class ErrorHandler:
    """Centralized error handling for Nimo platform"""

    # Predefined error codes and messages
    ERROR_CODES = {
        # Network errors
        "NETWORK_CONNECTION_FAILED": NimoError(
            code="NETWORK_CONNECTION_FAILED",
            message="Failed to connect to blockchain network",
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.HIGH,
            recoverable=True
        ),
        "NETWORK_TIMEOUT": NimoError(
            code="NETWORK_TIMEOUT",
            message="Network request timed out",
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            recoverable=True
        ),

        # Blockchain errors
        "BLOCKCHAIN_TRANSACTION_FAILED": NimoError(
            code="BLOCKCHAIN_TRANSACTION_FAILED",
            message="Blockchain transaction failed",
            category=ErrorCategory.BLOCKCHAIN,
            severity=ErrorSeverity.HIGH,
            recoverable=False
        ),
        "BLOCKCHAIN_INSUFFICIENT_FUNDS": NimoError(
            code="BLOCKCHAIN_INSUFFICIENT_FUNDS",
            message="Insufficient funds for transaction",
            category=ErrorCategory.BLOCKCHAIN,
            severity=ErrorSeverity.MEDIUM,
            recoverable=False
        ),
        "BLOCKCHAIN_INVALID_ADDRESS": NimoError(
            code="BLOCKCHAIN_INVALID_ADDRESS",
            message="Invalid blockchain address format",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            recoverable=False
        ),

        # Service errors
        "SERVICE_UNAVAILABLE": NimoError(
            code="SERVICE_UNAVAILABLE",
            message="Blockchain service is currently unavailable",
            category=ErrorCategory.SERVICE,
            severity=ErrorSeverity.HIGH,
            recoverable=True
        ),
        "SERVICE_CONFIGURATION_ERROR": NimoError(
            code="SERVICE_CONFIGURATION_ERROR",
            message="Service configuration error",
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.CRITICAL,
            recoverable=False
        ),

        # Validation errors
        "VALIDATION_MISSING_FIELD": NimoError(
            code="VALIDATION_MISSING_FIELD",
            message="Required field is missing",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            recoverable=False
        ),
        "VALIDATION_INVALID_FORMAT": NimoError(
            code="VALIDATION_INVALID_FORMAT",
            message="Invalid data format",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            recoverable=False
        ),

        # Authentication/Authorization errors
        "AUTH_UNAUTHORIZED": NimoError(
            code="AUTH_UNAUTHORIZED",
            message="Unauthorized access",
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.MEDIUM,
            recoverable=False
        ),
        "AUTH_FORBIDDEN": NimoError(
            code="AUTH_FORBIDDEN",
            message="Access forbidden",
            category=ErrorCategory.AUTHORIZATION,
            severity=ErrorSeverity.MEDIUM,
            recoverable=False
        )
    }

    def __init__(self, service_name: str):
        """Initialize error handler for a specific service"""
        self.service_name = service_name
        self.logger = logging.getLogger(f"error_handler_{service_name}")

    def create_error(self,
                    code: str,
                    message: Optional[str] = None,
                    details: Optional[Dict[str, Any]] = None,
                    operation: Optional[str] = None) -> NimoError:
        """Create a standardized error"""
        if code in self.ERROR_CODES:
            base_error = self.ERROR_CODES[code]
            return NimoError(
                code=base_error.code,
                message=message or base_error.message,
                category=base_error.category,
                severity=base_error.severity,
                details=details,
                service=self.service_name,
                operation=operation,
                recoverable=base_error.recoverable
            )
        else:
            # Create custom error
            return NimoError(
                code=code,
                message=message or "Unknown error occurred",
                category=ErrorCategory.UNKNOWN,
                severity=ErrorSeverity.MEDIUM,
                details=details,
                service=self.service_name,
                operation=operation,
                recoverable=True
            )

    def handle_exception(self,
                        exception: Exception,
                        operation: Optional[str] = None,
                        context: Optional[Dict[str, Any]] = None) -> NimoError:
        """Handle exceptions and convert to standardized errors"""
        error_message = str(exception)
        error_type = type(exception).__name__

        # Log the exception
        self.logger.error(f"Exception in {operation or 'unknown'}: {error_type}: {error_message}",
                         extra={"context": context, "exception": exception})

        # Map common exceptions to error codes
        if "connection" in error_message.lower() or "network" in error_message.lower():
            return self.create_error(
                "NETWORK_CONNECTION_FAILED",
                message=f"Network error: {error_message}",
                details={"original_error": error_message, "error_type": error_type},
                operation=operation
            )
        elif "insufficient funds" in error_message.lower():
            return self.create_error(
                "BLOCKCHAIN_INSUFFICIENT_FUNDS",
                details={"original_error": error_message, "error_type": error_type},
                operation=operation
            )
        elif "timeout" in error_message.lower():
            return self.create_error(
                "NETWORK_TIMEOUT",
                details={"original_error": error_message, "error_type": error_type},
                operation=operation
            )
        else:
            return self.create_error(
                "BLOCKCHAIN_TRANSACTION_FAILED",
                message=f"Unexpected error: {error_message}",
                details={"original_error": error_message, "error_type": error_type},
                operation=operation
            )

    def to_response(self, error: NimoError, http_status: Optional[int] = None) -> tuple:
        """Convert error to Flask JSON response"""
        if http_status is None:
            # Map severity to HTTP status
            status_map = {
                ErrorSeverity.LOW: 400,
                ErrorSeverity.MEDIUM: 400,
                ErrorSeverity.HIGH: 500,
                ErrorSeverity.CRITICAL: 500
            }
            http_status = status_map.get(error.severity, 500)

        response_data = {
            "success": False,
            "error": {
                "code": error.code,
                "message": error.message,
                "category": error.category.value,
                "severity": error.severity.value,
                "service": error.service,
                "operation": error.operation,
                "recoverable": error.recoverable
            }
        }

        if error.details:
            response_data["error"]["details"] = error.details

        return jsonify(response_data), http_status

    def log_error(self, error: NimoError, level: int = logging.ERROR):
        """Log an error with appropriate level"""
        self.logger.log(level, f"Error {error.code}: {error.message}",
                       extra={
                           "error_code": error.code,
                           "category": error.category.value,
                           "severity": error.severity.value,
                           "service": error.service,
                           "operation": error.operation,
                           "details": error.details
                       })

# Global error handler instances
blockchain_error_handler = ErrorHandler("blockchain")
cardano_error_handler = ErrorHandler("cardano")

def handle_service_error(service_name: str, exception: Exception, operation: Optional[str] = None) -> NimoError:
    """Convenience function to handle service errors"""
    handler = ErrorHandler(service_name)
    return handler.handle_exception(exception, operation)

def create_service_response(success: bool,
                           data: Optional[Any] = None,
                           error: Optional[NimoError] = None,
                           http_status: Optional[int] = None) -> tuple:
    """Create standardized service response"""
    if success:
        response_data = {
            "success": True,
            "data": data
        }
        return jsonify(response_data), http_status or 200
    else:
        if error:
            handler = ErrorHandler(error.service or "unknown")
            return handler.to_response(error, http_status)
        else:
            # Generic error response
            response_data = {
                "success": False,
                "error": {
                    "code": "UNKNOWN_ERROR",
                    "message": "An unknown error occurred",
                    "category": "unknown",
                    "severity": "medium"
                }
            }
            return jsonify(response_data), http_status or 500