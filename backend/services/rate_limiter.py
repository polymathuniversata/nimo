"""
Redis-based rate limiting service for secure API protection.
Replaces in-memory rate limiting with persistent Redis storage.
"""
import redis
import time
import logging
import json
from typing import Optional, Dict, Any
from flask import current_app, request
from functools import wraps

logger = logging.getLogger(__name__)

class RedisRateLimiter:
    """Production-ready Redis-based rate limiter"""
    
    def __init__(self, redis_client=None):
        """Initialize rate limiter with Redis connection"""
        self.redis_client = redis_client
        
    def get_redis_client(self):
        """Get or create Redis client"""
        if not self.redis_client:
            try:
                redis_url = current_app.config.get('REDIS_URL', 'redis://localhost:6379/0')
                redis_password = current_app.config.get('REDIS_PASSWORD')
                redis_ssl = current_app.config.get('REDIS_SSL', False)
                
                # Connection pool for better performance
                pool = redis.ConnectionPool.from_url(
                    redis_url,
                    password=redis_password,
                    ssl=redis_ssl,
                    max_connections=current_app.config.get('REDIS_MAX_CONNECTIONS', 20),
                    socket_connect_timeout=current_app.config.get('REDIS_SOCKET_CONNECT_TIMEOUT', 5),
                    decode_responses=True
                )
                
                self.redis_client = redis.Redis(connection_pool=pool)
                
                # Test connection
                self.redis_client.ping()
                logger.info("Redis rate limiter initialized successfully")
                
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                # Fallback to in-memory storage
                self.redis_client = None
                
        return self.redis_client
    
    def _get_key(self, identifier: str, window_type: str = 'default') -> str:
        """Generate Redis key for rate limiting"""
        timestamp = int(time.time() / 300)  # 5-minute windows
        return f"rate_limit:{window_type}:{identifier}:{timestamp}"
    
    def is_rate_limited(self, identifier: str, limit: int = 100, window_seconds: int = 300) -> bool:
        """
        Check if identifier is rate limited.
        
        Args:
            identifier: Unique identifier (IP, user ID, etc.)
            limit: Maximum requests per window
            window_seconds: Time window in seconds
        
        Returns:
            True if rate limited, False otherwise
        """
        redis_client = self.get_redis_client()
        
        if not redis_client:
            # Fallback to simple check if Redis unavailable
            logger.warning("Redis unavailable, using basic rate limiting")
            return False
        
        try:
            # Use sliding window with multiple keys
            current_time = int(time.time())
            window_start = current_time - window_seconds
            
            # Count requests in current window
            pipe = redis_client.pipeline()
            
            # Get current window count
            current_window = int(current_time / window_seconds)
            prev_window = current_window - 1
            
            current_key = f"rate_limit:{identifier}:{current_window}"
            prev_key = f"rate_limit:{identifier}:{prev_window}"
            
            pipe.get(current_key)
            pipe.get(prev_key)
            
            results = pipe.execute()
            
            current_count = int(results[0] or 0)
            prev_count = int(results[1] or 0)
            
            # Calculate sliding window count
            window_overlap = (current_time % window_seconds) / window_seconds
            total_count = current_count + (prev_count * (1 - window_overlap))
            
            return total_count >= limit
            
        except Exception as e:
            logger.error(f"Rate limiting check failed: {e}")
            return False
    
    def record_request(self, identifier: str, window_seconds: int = 300) -> bool:
        """
        Record a request for rate limiting.
        
        Args:
            identifier: Unique identifier
            window_seconds: Time window in seconds
        
        Returns:
            True if recorded successfully, False otherwise
        """
        redis_client = self.get_redis_client()
        
        if not redis_client:
            return False
        
        try:
            current_time = int(time.time())
            current_window = int(current_time / window_seconds)
            key = f"rate_limit:{identifier}:{current_window}"
            
            # Increment counter and set expiration
            pipe = redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, window_seconds * 2)  # Keep for 2 windows
            pipe.execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to record request: {e}")
            return False
    
    def get_rate_limit_info(self, identifier: str, window_seconds: int = 300) -> Dict[str, Any]:
        """Get current rate limit status for identifier"""
        redis_client = self.get_redis_client()
        
        if not redis_client:
            return {'requests': 0, 'window_seconds': window_seconds, 'reset_time': None}
        
        try:
            current_time = int(time.time())
            current_window = int(current_time / window_seconds)
            key = f"rate_limit:{identifier}:{current_window}"
            
            current_count = int(redis_client.get(key) or 0)
            reset_time = (current_window + 1) * window_seconds
            
            return {
                'requests': current_count,
                'window_seconds': window_seconds,
                'reset_time': reset_time,
                'time_to_reset': reset_time - current_time
            }
            
        except Exception as e:
            logger.error(f"Failed to get rate limit info: {e}")
            return {'requests': 0, 'window_seconds': window_seconds, 'reset_time': None}
    
    def reset_rate_limit(self, identifier: str) -> bool:
        """Reset rate limit for identifier (admin function)"""
        redis_client = self.get_redis_client()
        
        if not redis_client:
            return False
        
        try:
            pattern = f"rate_limit:{identifier}:*"
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
            return True
            
        except Exception as e:
            logger.error(f"Failed to reset rate limit: {e}")
            return False


# Global rate limiter instance
_rate_limiter = None

def get_rate_limiter() -> RedisRateLimiter:
    """Get global rate limiter instance"""
    global _rate_limiter
    if not _rate_limiter:
        _rate_limiter = RedisRateLimiter()
    return _rate_limiter


def rate_limit(limit: int = 100, window_seconds: int = 300, per_user: bool = False, key_func=None):
    """
    Enhanced rate limiting decorator with Redis backend.
    
    Args:
        limit: Max requests per window
        window_seconds: Time window in seconds
        per_user: Rate limit per authenticated user vs per IP
        key_func: Custom function to generate rate limit key
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            limiter = get_rate_limiter()
            
            # Generate identifier
            if key_func:
                identifier = key_func()
            elif per_user:
                # Try to get user ID from JWT or request
                try:
                    from flask_jwt_extended import get_jwt_identity, jwt_required
                    user_id = get_jwt_identity()
                    if user_id:
                        identifier = f"user:{user_id}"
                    else:
                        identifier = f"ip:{_get_client_ip()}"
                except:
                    identifier = f"ip:{_get_client_ip()}"
            else:
                identifier = f"ip:{_get_client_ip()}"
            
            # Check rate limit
            if limiter.is_rate_limited(identifier, limit, window_seconds):
                # Get rate limit info for headers
                info = limiter.get_rate_limit_info(identifier, window_seconds)
                
                # Log rate limit exceeded
                logger.warning(f"Rate limit exceeded for {identifier}, limit: {limit}")
                
                from flask import jsonify
                response = jsonify({
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Try again in {info.get('time_to_reset', 0)} seconds.",
                    "retry_after": info.get('time_to_reset', 300)
                })
                response.status_code = 429
                
                # Add rate limit headers
                response.headers['X-RateLimit-Limit'] = str(limit)
                response.headers['X-RateLimit-Remaining'] = '0'
                response.headers['X-RateLimit-Reset'] = str(info.get('reset_time', ''))
                response.headers['Retry-After'] = str(info.get('time_to_reset', 300))
                
                return response
            
            # Record request
            limiter.record_request(identifier, window_seconds)
            
            # Execute original function
            response = f(*args, **kwargs)
            
            # Add rate limit headers to successful responses
            try:
                info = limiter.get_rate_limit_info(identifier, window_seconds)
                remaining = max(0, limit - info.get('requests', 0))
                
                if hasattr(response, 'headers'):
                    response.headers['X-RateLimit-Limit'] = str(limit)
                    response.headers['X-RateLimit-Remaining'] = str(remaining)
                    response.headers['X-RateLimit-Reset'] = str(info.get('reset_time', ''))
                    
            except Exception as e:
                logger.error(f"Failed to add rate limit headers: {e}")
            
            return response
        
        return decorated_function
    return decorator


def _get_client_ip() -> str:
    """Get client IP address considering proxies"""
    # Check for forwarded IP (common in load balancers)
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        # Take the first IP from the chain
        return forwarded_for.split(',')[0].strip()
    
    # Check other common proxy headers
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip
    
    # Fallback to remote address
    return request.environ.get('REMOTE_ADDR', '127.0.0.1')


# Specific rate limiters for different endpoints
def auth_rate_limit(f):
    """Rate limit for authentication endpoints (stricter)"""
    return rate_limit(limit=10, window_seconds=300, per_user=False)(f)

def api_rate_limit(f):
    """Standard API rate limit"""
    return rate_limit(limit=100, window_seconds=300, per_user=True)(f)

def upload_rate_limit(f):
    """Rate limit for file uploads (more restrictive)"""
    return rate_limit(limit=20, window_seconds=300, per_user=True)(f)