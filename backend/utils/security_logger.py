import logging
import logging.handlers
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from flask import request, g
import structlog
from pythonjsonlogger import jsonlogger

class SecurityLogger:
    """Enhanced security logging for Nimo backend"""

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize logging configuration for Flask app"""

        # Configure structured logging
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        # Create logs directory if it doesn't exist
        log_dir = os.path.join(os.getcwd(), 'logs')
        os.makedirs(log_dir, exist_ok=True)

        # Security events logger
        security_logger = logging.getLogger('security')
        security_logger.setLevel(logging.INFO)

        # File handler for security events
        security_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, 'security.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        security_handler.setLevel(logging.INFO)

        # JSON formatter for security logs
        security_formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s'
        )
        security_handler.setFormatter(security_formatter)
        security_logger.addHandler(security_handler)

        # Application logger
        app_logger = logging.getLogger('nimo')
        app_logger.setLevel(logging.INFO)

        # Console handler for development
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        app_logger.addHandler(console_handler)

        # File handler for application logs
        app_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, 'application.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        app_handler.setLevel(logging.INFO)
        app_handler.setFormatter(console_formatter)
        app_logger.addHandler(app_handler)

        # Error logger
        error_logger = logging.getLogger('error')
        error_logger.setLevel(logging.ERROR)

        error_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, 'error.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(security_formatter)
        error_logger.addHandler(error_handler)

        # Store loggers in app config
        app.security_logger = security_logger
        app.app_logger = app_logger
        app.error_logger = error_logger

        # Register request logging
        app.before_request(self._log_request_start)
        app.after_request(self._log_request_end)
        app.teardown_request(self._log_request_teardown)

    def _log_request_start(self):
        """Log request start with security context"""
        g.request_start_time = datetime.utcnow()
        g.request_id = request.headers.get('X-Request-ID', 'unknown')

        # Log security-relevant request details
        security_context = {
            'request_id': g.request_id,
            'method': request.method,
            'url': request.url,
            'remote_addr': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
            'content_length': request.headers.get('Content-Length', 0),
            'timestamp': g.request_start_time.isoformat()
        }

        # Log potential security threats
        if self._is_suspicious_request(request):
            self.app.security_logger.warning(
                'Suspicious request detected',
                extra=security_context
            )

    def _log_request_end(self, response):
        """Log request completion"""
        if hasattr(g, 'request_start_time'):
            duration = (datetime.utcnow() - g.request_start_time).total_seconds()

            log_data = {
                'request_id': getattr(g, 'request_id', 'unknown'),
                'method': request.method,
                'url': request.url,
                'status_code': response.status_code,
                'duration': duration,
                'response_length': len(response.get_data())
            }

            if response.status_code >= 400:
                self.app.error_logger.error(
                    f'Request failed: {response.status_code}',
                    extra=log_data
                )
            else:
                self.app.app_logger.info(
                    f'Request completed: {response.status_code}',
                    extra=log_data
                )

        return response

    def _log_request_teardown(self, exception):
        """Log request teardown and exceptions"""
        if exception:
            error_context = {
                'request_id': getattr(g, 'request_id', 'unknown'),
                'method': request.method,
                'url': request.url,
                'exception_type': type(exception).__name__,
                'exception_message': str(exception),
                'timestamp': datetime.utcnow().isoformat()
            }

            self.app.error_logger.error(
                'Unhandled exception in request',
                extra=error_context,
                exc_info=exception
            )

    def _is_suspicious_request(self, request) -> bool:
        """Check for suspicious request patterns"""
        suspicious_patterns = [
            # SQL injection attempts
            'union select',
            '1=1',
            'or 1=1',
            # XSS attempts
            '<script>',
            'javascript:',
            # Path traversal
            '../',
            '..\\',
            # Common attack patterns
            'admin',
            'config',
            'phpmyadmin'
        ]

        check_fields = [
            request.url,
            request.headers.get('User-Agent', ''),
            request.headers.get('Referer', '')
        ]

        for field in check_fields:
            if field:
                for pattern in suspicious_patterns:
                    if pattern.lower() in field.lower():
                        return True

        return False

    def log_security_event(self, event_type: str, details: Dict[str, Any],
                          severity: str = 'INFO', user_id: Optional[str] = None):
        """Log security events"""
        security_data = {
            'event_type': event_type,
            'severity': severity,
            'user_id': user_id,
            'details': details,
            'timestamp': datetime.utcnow().isoformat(),
            'source_ip': request.remote_addr if request else None
        }

        if severity == 'CRITICAL':
            self.app.security_logger.critical(event_type, extra=security_data)
        elif severity == 'ERROR':
            self.app.security_logger.error(event_type, extra=security_data)
        elif severity == 'WARNING':
            self.app.security_logger.warning(event_type, extra=security_data)
        else:
            self.app.security_logger.info(event_type, extra=security_data)

    def log_wallet_operation(self, operation: str, wallet_address: str,
                           amount: Optional[float] = None, success: bool = True):
        """Log wallet operations for audit trail"""
        operation_data = {
            'operation': operation,
            'wallet_address': wallet_address,
            'amount': amount,
            'success': success,
            'timestamp': datetime.utcnow().isoformat()
        }

        if success:
            self.app.app_logger.info(f'Wallet operation: {operation}', extra=operation_data)
        else:
            self.app.error_logger.error(f'Wallet operation failed: {operation}', extra=operation_data)

    def log_metta_operation(self, operation: str, details: Dict[str, Any],
                          success: bool = True):
        """Log MeTTa operations"""
        metta_data = {
            'operation': operation,
            'details': details,
            'success': success,
            'timestamp': datetime.utcnow().isoformat()
        }

        if success:
            self.app.app_logger.info(f'MeTTa operation: {operation}', extra=metta_data)
        else:
            self.app.error_logger.error(f'MeTTa operation failed: {operation}', extra=metta_data)