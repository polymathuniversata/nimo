"""
Security middleware for Flask application.
Implements various security measures including CORS, rate limiting, input validation, etc.
"""
from functools import wraps
from flask import request, jsonify, current_app, g
from flask_cors import CORS
import re
import time
import json
import logging
from typing import Dict, Any, Optional, List
from werkzeug.exceptions import RequestEntityTooLarge

# Configure security logger
security_logger = logging.getLogger('nimo.security')

class SecurityConfig:
    """Security configuration constants"""
    
    # Rate limiting
    DEFAULT_RATE_LIMIT = 100  # requests per window
    AUTH_RATE_LIMIT = 10      # auth requests per window
    RATE_LIMIT_WINDOW = 300   # 5 minutes
    
    # Request size limits
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    MAX_JSON_SIZE = 1024 * 1024             # 1MB for JSON
    
    # Input validation
    MAX_STRING_LENGTH = 10000
    MAX_ARRAY_LENGTH = 1000
    
    # CORS settings
    CORS_ORIGINS = [
        'http://localhost:3000',
        'http://localhost:5173',
        'http://localhost:4173',
        'https://nimo.platform'
    ]
    
    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';",
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    }

def init_security(app):
    """Initialize security middleware for the Flask app"""
    
    # Set request size limit
    app.config['MAX_CONTENT_LENGTH'] = SecurityConfig.MAX_CONTENT_LENGTH
    
    # Configure CORS
    CORS(app, 
         origins=SecurityConfig.CORS_ORIGINS,
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
         supports_credentials=True)
    
    # Add security headers to all responses
    @app.after_request
    def add_security_headers(response):
        for header, value in SecurityConfig.SECURITY_HEADERS.items():
            response.headers[header] = value
        return response
    
    # Request size validation
    @app.before_request
    def validate_request_size():
        if request.content_length and request.content_length > SecurityConfig.MAX_CONTENT_LENGTH:
            security_logger.warning(f"Request too large: {request.content_length} bytes from {request.remote_addr}")
            return jsonify({"error": "Request entity too large"}), 413
    
    # Log security events
    @app.before_request
    def log_request():
        if current_app.debug:
            security_logger.debug(f"Request: {request.method} {request.path} from {request.remote_addr}")

class RateLimiter:
    """Rate limiting implementation"""
    
    # In-memory storage (use Redis in production)
    _requests = {}
    
    @classmethod
    def _cleanup_old_requests(cls):
        """Remove old rate limit entries"""
        current_time = time.time()
        expired_keys = []
        
        for key, timestamps in cls._requests.items():
            cls._requests[key] = [
                ts for ts in timestamps 
                if current_time - ts <= SecurityConfig.RATE_LIMIT_WINDOW
            ]
            if not cls._requests[key]:
                expired_keys.append(key)
        
        for key in expired_keys:
            del cls._requests[key]
    
    @classmethod
    def is_rate_limited(cls, identifier: str, limit: int = None) -> bool:
        """Check if identifier is rate limited"""
        if limit is None:
            limit = SecurityConfig.DEFAULT_RATE_LIMIT
            
        cls._cleanup_old_requests()
        
        if identifier not in cls._requests:
            cls._requests[identifier] = []
        
        return len(cls._requests[identifier]) >= limit
    
    @classmethod
    def record_request(cls, identifier: str):
        """Record a request for rate limiting"""
        current_time = time.time()
        if identifier not in cls._requests:
            cls._requests[identifier] = []
        cls._requests[identifier].append(current_time)

def rate_limit(limit: int = None, per_user: bool = False):
    """
    Rate limiting decorator.
    
    Args:
        limit: Max requests per window (default from config)
        per_user: If True, rate limit per user, otherwise per IP
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Determine identifier
            if per_user and hasattr(g, 'current_user') and g.current_user:
                identifier = f"user:{g.current_user.id}"
            else:
                identifier = f"ip:{request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', '127.0.0.1'))}"
            
            # Check rate limit
            if RateLimiter.is_rate_limited(identifier, limit):
                security_logger.warning(f"Rate limit exceeded for {identifier}")
                return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429
            
            # Record request
            RateLimiter.record_request(identifier)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

class InputValidator:
    """Input validation utilities"""
    
    @staticmethod
    def validate_string(value: Any, max_length: int = None, pattern: str = None) -> bool:
        """Validate string input"""
        if not isinstance(value, str):
            return False
        
        if max_length is None:
            max_length = SecurityConfig.MAX_STRING_LENGTH
        
        if len(value) > max_length:
            return False
        
        if pattern and not re.match(pattern, value):
            return False
        
        return True
    
    @staticmethod
    def validate_array(value: Any, max_length: int = None) -> bool:
        """Validate array input"""
        if not isinstance(value, list):
            return False
        
        if max_length is None:
            max_length = SecurityConfig.MAX_ARRAY_LENGTH
        
        return len(value) <= max_length
    
    @staticmethod
    def validate_json_size(data: Dict[str, Any]) -> bool:
        """Validate JSON payload size"""
        try:
            json_str = json.dumps(data)
            return len(json_str.encode('utf-8')) <= SecurityConfig.MAX_JSON_SIZE
        except Exception:
            return False
    
    @staticmethod
    def sanitize_string(value: str) -> str:
        """Basic string sanitization"""
        if not isinstance(value, str):
            return ""
        
        # Remove null bytes and control characters
        value = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', value)
        
        # Limit length
        if len(value) > SecurityConfig.MAX_STRING_LENGTH:
            value = value[:SecurityConfig.MAX_STRING_LENGTH]
        
        return value.strip()
    
    @staticmethod
    def validate_wallet_address(address: str) -> bool:
        """Validate Ethereum wallet address"""
        if not isinstance(address, str):
            return False
        
        # Remove 0x prefix if present
        if address.startswith('0x'):
            address = address[2:]
        
        # Check if it's 40 hex characters
        return bool(re.match(r'^[0-9a-fA-F]{40}$', address))
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        if not isinstance(email, str):
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email)) and len(email) <= 254

def validate_input(validation_rules: Dict[str, Dict[str, Any]]):
    """
    Decorator for input validation.
    
    Example:
    @validate_input({
        'email': {'type': 'email', 'required': True},
        'name': {'type': 'string', 'max_length': 100, 'required': True},
        'skills': {'type': 'array', 'max_length': 20}
    })
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json(force=True) if request.is_json else {}
            
            if not isinstance(data, dict):
                security_logger.warning(f"Invalid JSON structure from {request.remote_addr}")
                return jsonify({"error": "Invalid JSON structure"}), 400
            
            # Validate JSON size
            if not InputValidator.validate_json_size(data):
                security_logger.warning(f"JSON payload too large from {request.remote_addr}")
                return jsonify({"error": "Request payload too large"}), 413
            
            # Validate each field
            for field, rules in validation_rules.items():
                value = data.get(field)
                
                # Check required fields
                if rules.get('required', False) and (value is None or value == ''):
                    return jsonify({"error": f"Field '{field}' is required"}), 400
                
                # Skip validation for optional empty fields
                if value is None or value == '':
                    continue
                
                # Validate by type
                field_type = rules.get('type', 'string')
                
                if field_type == 'string':
                    max_length = rules.get('max_length')
                    pattern = rules.get('pattern')
                    if not InputValidator.validate_string(value, max_length, pattern):
                        return jsonify({"error": f"Invalid format for field '{field}'"}), 400
                    # Sanitize the string
                    data[field] = InputValidator.sanitize_string(value)
                
                elif field_type == 'email':
                    if not InputValidator.validate_email(value):
                        return jsonify({"error": f"Invalid email format for field '{field}'"}), 400
                
                elif field_type == 'wallet_address':
                    if not InputValidator.validate_wallet_address(value):
                        return jsonify({"error": f"Invalid wallet address format for field '{field}'"}), 400
                
                elif field_type == 'array':
                    max_length = rules.get('max_length')
                    if not InputValidator.validate_array(value, max_length):
                        return jsonify({"error": f"Invalid array format for field '{field}'"}), 400
                
                elif field_type == 'integer':
                    if not isinstance(value, int):
                        try:
                            data[field] = int(value)
                        except (ValueError, TypeError):
                            return jsonify({"error": f"Invalid integer format for field '{field}'"}), 400
                
                elif field_type == 'float':
                    if not isinstance(value, (int, float)):
                        try:
                            data[field] = float(value)
                        except (ValueError, TypeError):
                            return jsonify({"error": f"Invalid number format for field '{field}'"}), 400
                
                # Additional validations
                if 'min_length' in rules and isinstance(value, str):
                    if len(value) < rules['min_length']:
                        return jsonify({"error": f"Field '{field}' must be at least {rules['min_length']} characters long"}), 400
            
            # Store validated data for the route to use
            g.validated_data = data
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def log_security_event(event_type: str, details: Dict[str, Any]):
    """Log security events"""
    log_data = {
        'timestamp': time.time(),
        'event_type': event_type,
        'ip': request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', '127.0.0.1')),
        'user_agent': request.headers.get('User-Agent', ''),
        'path': request.path,
        'method': request.method,
        **details
    }
    
    security_logger.warning(f"Security Event: {json.dumps(log_data)}")

class SecurityMonitor:
    """Monitor and detect suspicious activity"""
    
    # Suspicious patterns
    SQL_INJECTION_PATTERNS = [
        r"(\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bDROP\b|\bUNION\b)",
        r"(\bOR\b\s+\d+\s*=\s*\d+|\bAND\b\s+\d+\s*=\s*\d+)",
        r"(['\"]\s*;\s*--|\|\||&&)"
    ]
    
    XSS_PATTERNS = [
        r"<script[\s\S]*?>[\s\S]*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[\s\S]*?>",
    ]
    
    @classmethod
    def detect_sql_injection(cls, text: str) -> bool:
        """Detect potential SQL injection attempts"""
        if not isinstance(text, str):
            return False
        
        text_upper = text.upper()
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text_upper, re.IGNORECASE):
                return True
        return False
    
    @classmethod
    def detect_xss(cls, text: str) -> bool:
        """Detect potential XSS attempts"""
        if not isinstance(text, str):
            return False
        
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    @classmethod
    def scan_input(cls, data: Dict[str, Any]) -> List[str]:
        """Scan input for security threats"""
        threats = []
        
        def scan_value(value, key=""):
            if isinstance(value, str):
                if cls.detect_sql_injection(value):
                    threats.append(f"SQL injection detected in {key}")
                if cls.detect_xss(value):
                    threats.append(f"XSS attempt detected in {key}")
            elif isinstance(value, dict):
                for k, v in value.items():
                    scan_value(v, f"{key}.{k}" if key else k)
            elif isinstance(value, list):
                for i, v in enumerate(value):
                    scan_value(v, f"{key}[{i}]" if key else f"[{i}]")
        
        scan_value(data)
        return threats

def security_scan(f):
    """Decorator to scan requests for security threats"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.is_json:
            data = request.get_json(force=True)
            if isinstance(data, dict):
                threats = SecurityMonitor.scan_input(data)
                if threats:
                    log_security_event('security_threat_detected', {
                        'threats': threats,
                        'user_id': getattr(g, 'current_user', {}).get('id') if hasattr(g, 'current_user') else None
                    })
                    security_logger.error(f"Security threats detected: {threats}")
                    return jsonify({"error": "Invalid request content"}), 400
        
        return f(*args, **kwargs)
    
    return decorated_function