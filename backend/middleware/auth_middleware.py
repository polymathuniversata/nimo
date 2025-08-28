"""
Authentication middleware for Flask application.
Provides JWT token validation and user context injection.
"""
from functools import wraps
from flask import request, jsonify, g, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from models.user import User
import time

class AuthenticationError(Exception):
    """Custom exception for authentication errors"""
    def __init__(self, message, status_code=401):
        super().__init__(message)
        self.status_code = status_code

def require_auth(f):
    """
    Decorator to require valid JWT authentication for a route.
    Injects the current user into g.current_user.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Verify JWT token
            verify_jwt_in_request()
            
            # Get user ID from token
            user_id = get_jwt_identity()
            if not user_id:
                raise AuthenticationError("Invalid token: no user identity")
            
            # Get user from database
            user = User.query.get(int(user_id))
            if not user:
                raise AuthenticationError("User not found")
            
            # Store user in Flask's g context
            g.current_user = user
            
            # Check if token is blacklisted (you would implement this with Redis in production)
            # For now, we'll skip blacklist checking
            
            return f(*args, **kwargs)
            
        except AuthenticationError as e:
            current_app.logger.warning(f"Authentication failed: {e}")
            return jsonify({"error": str(e)}), e.status_code
        except Exception as e:
            current_app.logger.error(f"Auth middleware error: {e}")
            return jsonify({"error": "Authentication failed"}), 401
    
    return decorated_function

def optional_auth(f):
    """
    Decorator that adds user context if JWT is provided but doesn't require it.
    Sets g.current_user to None if no valid token is provided.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Try to verify JWT token (won't raise exception if missing)
            verify_jwt_in_request(optional=True)
            
            # Get user ID from token if present
            user_id = get_jwt_identity()
            
            if user_id:
                # Get user from database
                user = User.query.get(int(user_id))
                g.current_user = user
            else:
                g.current_user = None
                
        except Exception as e:
            # Log but don't fail if optional auth fails
            current_app.logger.debug(f"Optional auth failed: {e}")
            g.current_user = None
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_wallet_auth(f):
    """
    Decorator that requires the user to be authenticated via wallet.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # First require basic auth
            verify_jwt_in_request()
            
            # Get user ID from token
            user_id = get_jwt_identity()
            if not user_id:
                raise AuthenticationError("Invalid token: no user identity")
            
            # Get user from database
            user = User.query.get(int(user_id))
            if not user:
                raise AuthenticationError("User not found")
            
            # Check if user is wallet-authenticated
            if user.auth_method != 'wallet' or not user.wallet_address:
                raise AuthenticationError("Wallet authentication required")
            
            # Store user in Flask's g context
            g.current_user = user
            
            return f(*args, **kwargs)
            
        except AuthenticationError as e:
            current_app.logger.warning(f"Wallet authentication failed: {e}")
            return jsonify({"error": str(e)}), e.status_code
        except Exception as e:
            current_app.logger.error(f"Wallet auth middleware error: {e}")
            return jsonify({"error": "Wallet authentication failed"}), 401
    
    return decorated_function

def get_current_user():
    """
    Helper function to get the current authenticated user.
    Returns None if no user is authenticated.
    """
    return getattr(g, 'current_user', None)

def is_authenticated():
    """
    Helper function to check if a user is currently authenticated.
    """
    return get_current_user() is not None

def is_wallet_authenticated():
    """
    Helper function to check if current user is wallet authenticated.
    """
    user = get_current_user()
    return user is not None and user.auth_method == 'wallet' and user.wallet_address

class TokenBlacklist:
    """
    Token blacklist management.
    In production, this should use Redis or a database.
    """
    
    # In-memory blacklist (use Redis in production)
    _blacklisted_tokens = set()
    _blacklisted_users = set()  # For invalidating all tokens for a user
    
    @classmethod
    def blacklist_token(cls, jti):
        """Add a token to the blacklist"""
        cls._blacklisted_tokens.add(jti)
    
    @classmethod
    def blacklist_user_tokens(cls, user_id):
        """Blacklist all tokens for a user (for logout from all devices)"""
        cls._blacklisted_users.add(str(user_id))
    
    @classmethod
    def is_token_blacklisted(cls, jti, user_id=None):
        """Check if a token is blacklisted"""
        if jti in cls._blacklisted_tokens:
            return True
        if user_id and str(user_id) in cls._blacklisted_users:
            return True
        return False
    
    @classmethod
    def remove_user_from_blacklist(cls, user_id):
        """Remove user from blacklist (useful for account reactivation)"""
        cls._blacklisted_users.discard(str(user_id))

# JWT callback for checking blacklisted tokens
def check_if_token_revoked(jwt_header, jwt_payload):
    """
    Callback function to check if JWT token is revoked.
    This should be registered with flask_jwt_extended.
    """
    jti = jwt_payload['jti']
    user_id = jwt_payload['sub']  # subject is the user ID
    
    return TokenBlacklist.is_token_blacklisted(jti, user_id)

# Rate limiting middleware
class AuthRateLimit:
    """Rate limiting for authentication endpoints"""
    
    # In-memory rate limiting (use Redis in production)
    _requests = {}
    MAX_REQUESTS = 10  # requests per window
    WINDOW_SIZE = 300   # 5 minutes
    
    @classmethod
    def _cleanup_old_requests(cls):
        """Clean up old rate limit entries"""
        current_time = time.time()
        expired_ips = [
            ip for ip, timestamps in cls._requests.items()
            if all(current_time - ts > cls.WINDOW_SIZE for ts in timestamps)
        ]
        for ip in expired_ips:
            del cls._requests[ip]
    
    @classmethod
    def is_rate_limited(cls, ip_address):
        """Check if IP is rate limited"""
        cls._cleanup_old_requests()
        
        current_time = time.time()
        if ip_address not in cls._requests:
            cls._requests[ip_address] = []
        
        # Remove old requests outside window
        cls._requests[ip_address] = [
            ts for ts in cls._requests[ip_address]
            if current_time - ts <= cls.WINDOW_SIZE
        ]
        
        return len(cls._requests[ip_address]) >= cls.MAX_REQUESTS
    
    @classmethod
    def record_request(cls, ip_address):
        """Record an authentication request"""
        current_time = time.time()
        if ip_address not in cls._requests:
            cls._requests[ip_address] = []
        cls._requests[ip_address].append(current_time)

def rate_limit_auth(f):
    """Decorator to rate limit authentication endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get client IP
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', 
                                       request.environ.get('REMOTE_ADDR', '127.0.0.1'))
        
        # Check rate limit
        if AuthRateLimit.is_rate_limited(client_ip):
            current_app.logger.warning(f"Auth rate limit exceeded for IP: {client_ip}")
            return jsonify({"error": "Too many requests. Please try again later."}), 429
        
        # Record request
        AuthRateLimit.record_request(client_ip)
        
        return f(*args, **kwargs)
    
    return decorated_function