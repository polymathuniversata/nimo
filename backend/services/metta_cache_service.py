"""
Redis Caching Service for MeTTa Autonomous System

This module provides high-performance caching for MeTTa queries,
autonomous operations, and system state to improve response times
and reduce computational load.
"""

import redis
import json
import hashlib
import time
from typing import Any, Dict, Optional, List, Union
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class MeTTaCacheService:
    """Redis-based caching service for MeTTa autonomous operations"""

    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0,
                 password: Optional[str] = None, socket_timeout: int = 5):
        """Initialize Redis connection"""
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            socket_timeout=socket_timeout,
            decode_responses=True
        )

        # Test connection
        try:
            self.redis_client.ping()
            logger.info("✅ Redis connection established")
        except redis.ConnectionError:
            logger.warning("⚠️ Redis connection failed - using in-memory cache")
            self.redis_client = None

        # Cache TTL configurations (in seconds)
        self.cache_ttl = {
            'metta_query': 300,        # 5 minutes for MeTTa queries
            'contribution_verify': 600, # 10 minutes for verification results
            'reward_calculation': 1800, # 30 minutes for reward calculations
            'fraud_detection': 900,    # 15 minutes for fraud detection
            'predictive_analytics': 3600, # 1 hour for analytics
            'platform_metrics': 60,    # 1 minute for platform metrics
            'user_profile': 1800,      # 30 minutes for user profiles
            'system_state': 30,        # 30 seconds for system state
        }

        # In-memory fallback cache
        self.memory_cache = {}

    def _generate_cache_key(self, operation: str, params: Dict[str, Any]) -> str:
        """Generate a unique cache key for the operation and parameters"""
        # Sort parameters for consistent key generation
        sorted_params = json.dumps(params, sort_keys=True, default=str)
        key_content = f"{operation}:{sorted_params}"

        # Create SHA256 hash for the key
        key_hash = hashlib.sha256(key_content.encode()).hexdigest()[:16]
        return f"metta:{operation}:{key_hash}"

    def _serialize_value(self, value: Any) -> str:
        """Serialize value for Redis storage"""
        if isinstance(value, (dict, list)):
            return json.dumps(value, default=str)
        elif isinstance(value, (int, float, bool)):
            return str(value)
        else:
            return str(value)

    def _deserialize_value(self, value: str) -> Any:
        """Deserialize value from Redis storage"""
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    def get(self, operation: str, params: Dict[str, Any]) -> Optional[Any]:
        """Get cached result for operation"""
        cache_key = self._generate_cache_key(operation, params)

        try:
            if self.redis_client:
                cached_value = self.redis_client.get(cache_key)
                if cached_value:
                    logger.debug(f"Cache hit for {operation}")
                    return self._deserialize_value(cached_value)
            else:
                # Use in-memory cache
                cached_item = self.memory_cache.get(cache_key)
                if cached_item and cached_item['expires'] > time.time():
                    logger.debug(f"Memory cache hit for {operation}")
                    return cached_item['value']

        except Exception as e:
            logger.warning(f"Cache retrieval error: {e}")

        logger.debug(f"Cache miss for {operation}")
        return None

    def set(self, operation: str, params: Dict[str, Any], value: Any,
            ttl: Optional[int] = None) -> bool:
        """Set cached result for operation"""
        cache_key = self._generate_cache_key(operation, params)

        if ttl is None:
            ttl = self.cache_ttl.get(operation, 300)  # Default 5 minutes

        serialized_value = self._serialize_value(value)

        try:
            if self.redis_client:
                return self.redis_client.setex(cache_key, ttl, serialized_value)
            else:
                # Use in-memory cache
                self.memory_cache[cache_key] = {
                    'value': value,
                    'expires': time.time() + ttl
                }
                return True

        except Exception as e:
            logger.warning(f"Cache storage error: {e}")
            return False

    def delete(self, operation: str, params: Dict[str, Any]) -> bool:
        """Delete cached result for operation"""
        cache_key = self._generate_cache_key(operation, params)

        try:
            if self.redis_client:
                return bool(self.redis_client.delete(cache_key))
            else:
                # Use in-memory cache
                if cache_key in self.memory_cache:
                    del self.memory_cache[cache_key]
                    return True
                return False

        except Exception as e:
            logger.warning(f"Cache deletion error: {e}")
            return False

    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all cache keys matching a pattern"""
        try:
            if self.redis_client:
                # Use SCAN to find matching keys
                keys_to_delete = []
                for key in self.redis_client.scan_iter(f"metta:{pattern}:*"):
                    keys_to_delete.append(key)

                if keys_to_delete:
                    return self.redis_client.delete(*keys_to_delete)
                return 0
            else:
                # Use in-memory cache
                keys_to_delete = []
                for key in self.memory_cache:
                    if key.startswith(f"metta:{pattern}:"):
                        keys_to_delete.append(key)

                for key in keys_to_delete:
                    del self.memory_cache[key]

                return len(keys_to_delete)

        except Exception as e:
            logger.warning(f"Pattern invalidation error: {e}")
            return 0

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        try:
            if self.redis_client:
                info = self.redis_client.info()
                return {
                    'redis_connected': True,
                    'used_memory': info.get('used_memory_human', 'N/A'),
                    'connected_clients': info.get('connected_clients', 0),
                    'total_keys': self.redis_client.dbsize(),
                    'uptime_days': info.get('uptime_in_days', 0)
                }
            else:
                return {
                    'redis_connected': False,
                    'memory_cache_entries': len(self.memory_cache),
                    'cache_type': 'in-memory'
                }

        except Exception as e:
            logger.warning(f"Cache stats error: {e}")
            return {'error': str(e)}

    def clear_all_cache(self) -> bool:
        """Clear all cached data"""
        try:
            if self.redis_client:
                # Clear only MeTTa-related keys
                keys_to_delete = []
                for key in self.redis_client.scan_iter("metta:*"):
                    keys_to_delete.append(key)

                if keys_to_delete:
                    self.redis_client.delete(*keys_to_delete)
                return True
            else:
                # Clear in-memory cache
                self.memory_cache.clear()
                return True

        except Exception as e:
            logger.warning(f"Cache clear error: {e}")
            return False

    # Specific caching methods for autonomous operations

    def cache_metta_query(self, query: str, params: Dict[str, Any], result: Any) -> bool:
        """Cache MeTTa query results"""
        return self.set('metta_query', {'query': query, **params}, result)

    def get_metta_query(self, query: str, params: Dict[str, Any]) -> Optional[Any]:
        """Get cached MeTTa query results"""
        return self.get('metta_query', {'query': query, **params})

    def cache_contribution_verification(self, contribution_id: str, result: Dict[str, Any]) -> bool:
        """Cache contribution verification results"""
        return self.set('contribution_verify', {'contribution_id': contribution_id}, result)

    def get_contribution_verification(self, contribution_id: str) -> Optional[Dict[str, Any]]:
        """Get cached contribution verification"""
        return self.get('contribution_verify', {'contribution_id': contribution_id})

    def cache_reward_calculation(self, contribution_id: str, quality_score: float,
                               impact_score: float, result: Dict[str, Any]) -> bool:
        """Cache reward calculation results"""
        params = {
            'contribution_id': contribution_id,
            'quality_score': quality_score,
            'impact_score': impact_score
        }
        return self.set('reward_calculation', params, result)

    def get_reward_calculation(self, contribution_id: str, quality_score: float,
                             impact_score: float) -> Optional[Dict[str, Any]]:
        """Get cached reward calculation"""
        params = {
            'contribution_id': contribution_id,
            'quality_score': quality_score,
            'impact_score': impact_score
        }
        return self.get('reward_calculation', params)

    def cache_fraud_detection(self, contribution_id: str, result: Dict[str, Any]) -> bool:
        """Cache fraud detection results"""
        return self.set('fraud_detection', {'contribution_id': contribution_id}, result)

    def get_fraud_detection(self, contribution_id: str) -> Optional[Dict[str, Any]]:
        """Get cached fraud detection results"""
        return self.get('fraud_detection', {'contribution_id': contribution_id})

    def cache_predictive_analytics(self, entity_id: str, prediction_type: str,
                                 result: Dict[str, Any]) -> bool:
        """Cache predictive analytics results"""
        params = {'entity_id': entity_id, 'prediction_type': prediction_type}
        return self.set('predictive_analytics', params, result)

    def get_predictive_analytics(self, entity_id: str, prediction_type: str) -> Optional[Dict[str, Any]]:
        """Get cached predictive analytics"""
        params = {'entity_id': entity_id, 'prediction_type': prediction_type}
        return self.get('predictive_analytics', params)

    def cache_platform_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Cache platform metrics"""
        return self.set('platform_metrics', {}, metrics, ttl=60)  # 1 minute TTL

    def get_platform_metrics(self) -> Optional[Dict[str, Any]]:
        """Get cached platform metrics"""
        return self.get('platform_metrics', {})

    def invalidate_user_cache(self, user_id: str) -> int:
        """Invalidate all cache entries for a specific user"""
        return self.invalidate_pattern(f"*{user_id}*")

    def invalidate_contribution_cache(self, contribution_id: str) -> int:
        """Invalidate all cache entries for a specific contribution"""
        return self.invalidate_pattern(f"*{contribution_id}*")

    def warmup_cache(self, operations: List[Dict[str, Any]]) -> Dict[str, int]:
        """Warm up cache with frequently accessed data"""
        success_count = 0
        error_count = 0

        for operation in operations:
            try:
                operation_type = operation.get('type')
                params = operation.get('params', {})
                result = operation.get('result')

                if operation_type and result:
                    self.set(operation_type, params, result)
                    success_count += 1
                else:
                    error_count += 1

            except Exception as e:
                logger.warning(f"Cache warmup error: {e}")
                error_count += 1

        return {
            'successful': success_count,
            'errors': error_count,
            'total': len(operations)
        }

# Global cache service instance
_cache_service = None

def get_cache_service() -> MeTTaCacheService:
    """Get or create global cache service instance"""
    global _cache_service
    if _cache_service is None:
        _cache_service = MeTTaCacheService()
    return _cache_service

# Convenience functions for easy integration
def cache_result(operation: str, params: Dict[str, Any], result: Any, ttl: Optional[int] = None) -> bool:
    """Cache a result with automatic service management"""
    return get_cache_service().set(operation, params, result, ttl)

def get_cached_result(operation: str, params: Dict[str, Any]) -> Optional[Any]:
    """Get a cached result with automatic service management"""
    return get_cache_service().get(operation, params)

def invalidate_cache_pattern(pattern: str) -> int:
    """Invalidate cache entries matching a pattern"""
    return get_cache_service().invalidate_pattern(pattern)

if __name__ == "__main__":
    # Test the cache service
    cache = MeTTaCacheService()

    # Test basic operations
    test_params = {"user_id": "test123", "operation": "verify"}
    test_result = {"verified": True, "confidence": 0.85}

    # Test set/get
    cache.set("test_operation", test_params, test_result)
    cached_result = cache.get("test_operation", test_params)

    print("Cache test:", "PASSED" if cached_result == test_result else "FAILED")

    # Test cache stats
    stats = cache.get_cache_stats()
    print("Cache stats:", stats)