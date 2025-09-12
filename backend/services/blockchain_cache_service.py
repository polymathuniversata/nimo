"""
Blockchain Data Caching Service

Implements Redis-based caching for blockchain data to improve performance
and reduce the number of on-chain queries.
"""

import json
import redis
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from flask import current_app

class BlockchainCacheService:
    """Redis-based caching service for blockchain data"""

    def __init__(self, redis_url: str = None):
        """Initialize Redis cache service"""
        self.redis_url = redis_url or 'redis://localhost:6379/0'
        self.redis_client = None
        self.cache_enabled = True
        self.default_ttl = 300  # 5 minutes default TTL

        # Cache key prefixes
        self.prefixes = {
            'user': 'user:',
            'contribution': 'contrib:',
            'token_balance': 'balance:',
            'transaction': 'tx:',
            'analytics': 'analytics:',
            'blockchain_data': 'blockchain:'
        }

        self._connect_redis()

    def _connect_redis(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            # Test connection
            self.redis_client.ping()
            current_app.logger.info("Redis cache connected successfully")
        except Exception as e:
            current_app.logger.warning(f"Redis connection failed: {e}")
            self.cache_enabled = False

    def _generate_key(self, prefix: str, identifier: str) -> str:
        """Generate cache key"""
        return f"{self.prefixes.get(prefix, '')}{identifier}"

    def _serialize_data(self, data: Any) -> str:
        """Serialize data for Redis storage"""
        if isinstance(data, (dict, list)):
            return json.dumps(data)
        return str(data)

    def _deserialize_data(self, data: str) -> Any:
        """Deserialize data from Redis storage"""
        try:
            return json.loads(data)
        except (json.JSONDecodeError, TypeError):
            return data

    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set cache value"""
        if not self.cache_enabled or not self.redis_client:
            return False

        try:
            serialized_value = self._serialize_data(value)
            ttl_value = ttl or self.default_ttl
            return self.redis_client.setex(key, ttl_value, serialized_value)
        except Exception as e:
            current_app.logger.warning(f"Cache set failed: {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """Get cache value"""
        if not self.cache_enabled or not self.redis_client:
            return None

        try:
            value = self.redis_client.get(key)
            if value:
                return self._deserialize_data(value)
            return None
        except Exception as e:
            current_app.logger.warning(f"Cache get failed: {e}")
            return None

    def delete(self, key: str) -> bool:
        """Delete cache key"""
        if not self.cache_enabled or not self.redis_client:
            return False

        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            current_app.logger.warning(f"Cache delete failed: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if cache key exists"""
        if not self.cache_enabled or not self.redis_client:
            return False

        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            current_app.logger.warning(f"Cache exists check failed: {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.cache_enabled or not self.redis_client:
            return 0

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            current_app.logger.warning(f"Cache clear pattern failed: {e}")
            return 0

    # User-specific cache methods
    def get_user_profile(self, user_id: int) -> Optional[Dict]:
        """Get cached user profile"""
        key = self._generate_key('user', f"profile:{user_id}")
        return self.get(key)

    def set_user_profile(self, user_id: int, profile: Dict, ttl: int = 600) -> bool:
        """Cache user profile (10 minutes TTL)"""
        key = self._generate_key('user', f"profile:{user_id}")
        return self.set(key, profile, ttl)

    def invalidate_user_profile(self, user_id: int) -> bool:
        """Invalidate user profile cache"""
        key = self._generate_key('user', f"profile:{user_id}")
        return self.delete(key)

    # Contribution-specific cache methods
    def get_user_contributions(self, user_id: int, page: int = 1, filters: Dict = None) -> Optional[Dict]:
        """Get cached user contributions"""
        # Security: Use SHA-256 instead of weak MD5 hash
        filter_hash = hashlib.sha256(json.dumps(filters or {}, sort_keys=True).encode()).hexdigest()[:16]
        key = self._generate_key('contribution', f"user:{user_id}:page:{page}:filters:{filter_hash}")
        return self.get(key)

    def set_user_contributions(self, user_id: int, contributions: Dict, page: int = 1, filters: Dict = None, ttl: int = 300) -> bool:
        """Cache user contributions (5 minutes TTL)"""
        # Security: Use SHA-256 instead of weak MD5 hash
        filter_hash = hashlib.sha256(json.dumps(filters or {}, sort_keys=True).encode()).hexdigest()[:16]
        key = self._generate_key('contribution', f"user:{user_id}:page:{page}:filters:{filter_hash}")
        return self.set(key, contributions, ttl)

    def invalidate_user_contributions(self, user_id: int) -> int:
        """Invalidate all contribution caches for user"""
        pattern = self._generate_key('contribution', f"user:{user_id}:*")
        return self.clear_pattern(pattern)

    # Token-specific cache methods
    def get_token_balance(self, user_id: int) -> Optional[Dict]:
        """Get cached token balance"""
        key = self._generate_key('token_balance', f"user:{user_id}")
        return self.get(key)

    def set_token_balance(self, user_id: int, balance: Dict, ttl: int = 60) -> bool:
        """Cache token balance (1 minute TTL)"""
        key = self._generate_key('token_balance', f"user:{user_id}")
        return self.set(key, balance, ttl)

    def invalidate_token_balance(self, user_id: int) -> bool:
        """Invalidate token balance cache"""
        key = self._generate_key('token_balance', f"user:{user_id}")
        return self.delete(key)

    # Transaction-specific cache methods
    def get_transaction_history(self, user_id: int, limit: int = 50) -> Optional[List]:
        """Get cached transaction history"""
        key = self._generate_key('transaction', f"user:{user_id}:limit:{limit}")
        return self.get(key)

    def set_transaction_history(self, user_id: int, transactions: List, limit: int = 50, ttl: int = 300) -> bool:
        """Cache transaction history (5 minutes TTL)"""
        key = self._generate_key('transaction', f"user:{user_id}:limit:{limit}")
        return self.set(key, transactions, ttl)

    def invalidate_transaction_history(self, user_id: int) -> int:
        """Invalidate transaction history cache"""
        pattern = self._generate_key('transaction', f"user:{user_id}:*")
        return self.clear_pattern(pattern)

    # Analytics cache methods
    def get_contribution_analytics(self, user_id: int, time_period: str = '30d') -> Optional[Dict]:
        """Get cached contribution analytics"""
        key = self._generate_key('analytics', f"contrib:{user_id}:{time_period}")
        return self.get(key)

    def set_contribution_analytics(self, user_id: int, analytics: Dict, time_period: str = '30d', ttl: int = 600) -> bool:
        """Cache contribution analytics (10 minutes TTL)"""
        key = self._generate_key('analytics', f"contrib:{user_id}:{time_period}")
        return self.set(key, analytics, ttl)

    def invalidate_contribution_analytics(self, user_id: int) -> int:
        """Invalidate contribution analytics cache"""
        pattern = self._generate_key('analytics', f"contrib:{user_id}:*")
        return self.clear_pattern(pattern)

    # Blockchain data cache methods
    def get_blockchain_data(self, data_type: str, identifier: str) -> Optional[Any]:
        """Get cached blockchain data"""
        key = self._generate_key('blockchain_data', f"{data_type}:{identifier}")
        return self.get(key)

    def set_blockchain_data(self, data_type: str, identifier: str, data: Any, ttl: int = 300) -> bool:
        """Cache blockchain data"""
        key = self._generate_key('blockchain_data', f"{data_type}:{identifier}")
        return self.set(key, data, ttl)

    def invalidate_blockchain_data(self, data_type: str, identifier: str = None) -> int:
        """Invalidate blockchain data cache"""
        if identifier:
            key = self._generate_key('blockchain_data', f"{data_type}:{identifier}")
            return self.delete(key)
        else:
            pattern = self._generate_key('blockchain_data', f"{data_type}:*")
            return self.clear_pattern(pattern)

    # Bulk operations
    def invalidate_user_cache(self, user_id: int) -> Dict[str, int]:
        """Invalidate all user-related caches"""
        results = {}

        # Invalidate user profile
        results['profile'] = self.invalidate_user_profile(user_id)

        # Invalidate contributions
        results['contributions'] = self.invalidate_user_contributions(user_id)

        # Invalidate token balance
        results['balance'] = self.invalidate_token_balance(user_id)

        # Invalidate transaction history
        results['transactions'] = self.invalidate_transaction_history(user_id)

        # Invalidate analytics
        results['analytics'] = self.invalidate_contribution_analytics(user_id)

        return results

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.cache_enabled or not self.redis_client:
            return {'enabled': False}

        try:
            info = self.redis_client.info()
            return {
                'enabled': True,
                'connected': True,
                'used_memory': info.get('used_memory_human'),
                'connected_clients': info.get('connected_clients'),
                'total_keys': self.redis_client.dbsize(),
                'uptime_days': info.get('uptime_in_days')
            }
        except Exception as e:
            return {
                'enabled': True,
                'connected': False,
                'error': str(e)
            }

    def clear_all_cache(self) -> bool:
        """Clear all cache data"""
        if not self.cache_enabled or not self.redis_client:
            return False

        try:
            return self.redis_client.flushdb()
        except Exception as e:
            current_app.logger.error(f"Cache clear all failed: {e}")
            return False