"""
Comprehensive logging configuration for Nimo Platform.
Sets up structured logging with proper levels, formatting, and handlers.
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Dict, Any
import json

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record):
        """Format log record as JSON"""
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                          'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process', 'getMessage']:
                log_entry[key] = value
        
        return json.dumps(log_entry)

class ContextualFormatter(logging.Formatter):
    """Human-readable formatter with context"""
    
    def format(self, record):
        """Format log record with context"""
        # Use a class-level cached formatter so we don't allocate a
        # new ``logging.Formatter`` instance for every single log call.
        # This saves significant CPU in high-traffic environments.
        base_format = '%(asctime)s - %(name)-20s - %(levelname)-8s - %(message)s'

        # Lazily create and cache the underlying formatter only once
        if not hasattr(self.__class__, "_base_formatter"):
            self.__class__._base_formatter = logging.Formatter(base_format)

        # Add context if available
        context_parts = []
        
        if hasattr(record, 'user_id'):
            context_parts.append(f"user:{record.user_id}")
        
        if hasattr(record, 'request_id'):
            context_parts.append(f"req:{record.request_id}")
        
        if hasattr(record, 'contribution_id'):
            context_parts.append(f"contrib:{record.contribution_id}")
        
        if context_parts:
            context_str = f"[{' | '.join(context_parts)}] "
            record.message = context_str + record.getMessage()
            record.msg = record.message
        
        # Re-use the cached formatter rather than constructing a new
        # object each call (which would be wasteful).
        formatter = self.__class__._base_formatter  # type: logging.Formatter
        return formatter.format(record)

def setup_logging(
    app_name: str = "nimo",
    log_level: str = "INFO",
    log_dir: str = "logs",
    enable_file_logging: bool = True,
    enable_json_logging: bool = False,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
):
    """
    Set up comprehensive logging configuration.
    
    Args:
        app_name: Name of the application
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        enable_file_logging: Whether to log to files
        enable_json_logging: Whether to use JSON format
        max_bytes: Maximum size of each log file
        backup_count: Number of backup files to keep
    """
    
    # Convert log level string to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create logs directory if it doesn't exist
    if enable_file_logging:
        os.makedirs(log_dir, exist_ok=True)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    
    if enable_json_logging:
        console_formatter = JSONFormatter()
    else:
        console_formatter = ContextualFormatter()
    
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handlers
    if enable_file_logging:
        # General application log
        app_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(log_dir, f"{app_name}.log"),
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        app_handler.setLevel(numeric_level)
        app_handler.setFormatter(console_formatter)
        root_logger.addHandler(app_handler)
        
        # Error log (ERROR and CRITICAL only)
        error_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(log_dir, f"{app_name}_error.log"),
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(console_formatter)
        root_logger.addHandler(error_handler)
        
        # Security log
        security_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(log_dir, f"{app_name}_security.log"),
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        security_handler.setLevel(logging.WARNING)
        security_formatter = JSONFormatter() if enable_json_logging else ContextualFormatter()
        security_handler.setFormatter(security_formatter)
        
        # Add security handler to security logger
        security_logger = logging.getLogger('nimo.security')
        security_logger.addHandler(security_handler)
        security_logger.setLevel(logging.WARNING)
    
    # Configure specific logger levels
    logger_configs = {
        'nimo': numeric_level,
        'nimo.auth': numeric_level,
        'nimo.security': logging.WARNING,
        'nimo.metta': numeric_level,
        'nimo.rewards': numeric_level,
        'nimo.blockchain': numeric_level,
        'werkzeug': logging.WARNING,  # Flask request logs
        'urllib3': logging.WARNING,   # HTTP client logs
        'requests': logging.WARNING,  # Requests library
    }
    
    for logger_name, level in logger_configs.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
    
    logging.info(f"Logging configured - Level: {log_level}, File logging: {enable_file_logging}, JSON: {enable_json_logging}")

class LogContext:
    """Context manager for adding contextual information to logs"""
    
    def __init__(self, **context):
        self.context = context
        self.old_factory = logging.getLogRecordFactory()
    
    def __enter__(self):
        def record_factory(*args, **kwargs):
            record = self.old_factory(*args, **kwargs)
            for key, value in self.context.items():
                setattr(record, key, value)
            return record
        
        logging.setLogRecordFactory(record_factory)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.setLogRecordFactory(self.old_factory)

def log_with_context(**context):
    """Decorator to add context to all logs within a function"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with LogContext(**context):
                return func(*args, **kwargs)
        return wrapper
    return decorator

class PerformanceLogger:
    """Logger for performance monitoring"""
    
    def __init__(self, logger_name: str = "nimo.performance"):
        self.logger = logging.getLogger(logger_name)
    
    def log_operation(
        self, 
        operation: str, 
        duration: float, 
        success: bool = True,
        **metadata
    ):
        """Log a timed operation"""
        log_data = {
            'operation': operation,
            'duration_ms': round(duration * 1000, 2),
            'success': success,
            **metadata
        }
        
        if success:
            self.logger.info(f"Operation completed: {operation}", extra=log_data)
        else:
            self.logger.warning(f"Operation failed: {operation}", extra=log_data)

class AuditLogger:
    """Logger for audit trail"""
    
    def __init__(self, logger_name: str = "nimo.audit"):
        self.logger = logging.getLogger(logger_name)
    
    def log_user_action(
        self,
        action: str,
        user_id: int,
        resource_type: str = None,
        resource_id: str = None,
        ip_address: str = None,
        user_agent: str = None,
        success: bool = True,
        **metadata
    ):
        """Log user actions for audit trail"""
        audit_data = {
            'action': action,
            'user_id': user_id,
            'success': success,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if resource_type:
            audit_data['resource_type'] = resource_type
        if resource_id:
            audit_data['resource_id'] = resource_id
        if ip_address:
            audit_data['ip_address'] = ip_address
        if user_agent:
            audit_data['user_agent'] = user_agent
        
        audit_data.update(metadata)
        
        level = logging.INFO if success else logging.WARNING
        self.logger.log(level, f"User action: {action}", extra=audit_data)

# Global instances
performance_logger = PerformanceLogger()
audit_logger = AuditLogger()

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name"""
    return logging.getLogger(name)

def log_exception(
    logger: logging.Logger, 
    message: str, 
    exc_info: Exception = None,
    **context
):
    """Log an exception with context"""
    with LogContext(**context):
        if exc_info:
            logger.exception(message, exc_info=exc_info)
        else:
            logger.exception(message)

# Request logging middleware integration
def add_request_logging(app):
    """Add request logging to Flask app"""
    request_logger = get_logger('nimo.requests')
    
    @app.before_request
    def log_request():
        from flask import request, g
        import uuid
        
        # Generate request ID
        g.request_id = str(uuid.uuid4())[:8]
        
        with LogContext(request_id=g.request_id):
            request_logger.info(
                f"{request.method} {request.path}",
                extra={
                    'method': request.method,
                    'path': request.path,
                    'remote_addr': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent'),
                    'content_length': request.content_length
                }
            )
    
    @app.after_request
    def log_response(response):
        from flask import g
        
        if hasattr(g, 'request_id'):
            with LogContext(request_id=g.request_id):
                request_logger.info(
                    f"Response {response.status_code}",
                    extra={
                        'status_code': response.status_code,
                        'content_length': response.content_length
                    }
                )
        
        return response