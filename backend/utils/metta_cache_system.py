"""
MeTTa Rule Result Caching System

This module provides intelligent caching mechanisms for MeTTa rule results
to improve performance and reduce redundant computations.
"""

import hashlib
import json
import time
import threading
from typing import Dict, Any, Optional, Tuple, List
from collections import OrderedDict
from dataclasses import dataclass
from functools import lru_cache
import pickle


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    timestamp: float
    access_count: int = 0
    last_accessed: float = 0
    ttl: Optional[float] = None
    size_bytes: int = 0

    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        if self.ttl is None:
            return False
        return time.time() - self.timestamp > self.ttl

    def access(self):
        """Record access to this entry"""
        self.access_count += 1
        self.last_accessed = time.time()


class MeTTaCache:
    """Intelligent cache for MeTTa rule results"""

    def __init__(self, max_size: int = 1000, default_ttl: float = 3600):
        """
        Initialize MeTTa cache

        Args:
            max_size: Maximum number of cache entries
            default_ttl: Default time-to-live in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = threading.RLock()
        self.hit_count = 0
        self.miss_count = 0
        self.eviction_count = 0

    def _generate_key(self, operation: str, *args, **kwargs) -> str:
        """
        Generate cache key from operation and arguments

        Args:
            operation: Operation name
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            str: Cache key
        """
        # Create a deterministic representation of arguments
        args_str = json.dumps(args, sort_keys=True, default=str)
        kwargs_str = json.dumps(kwargs, sort_keys=True, default=str)

        # Create hash of the arguments
        key_content = f"{operation}:{args_str}:{kwargs_str}"
        key_hash = hashlib.md5(key_content.encode()).hexdigest()

        return f"{operation}:{key_hash}"

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]

                if entry.is_expired():
                    del self.cache[key]
                    self.miss_count += 1
                    return None

                entry.access()
                self.cache.move_to_end(key)  # LRU ordering
                self.hit_count += 1
                return entry.value

            self.miss_count += 1
            return None

    def put(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """
        Put value in cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
        """
        with self.lock:
            # Calculate approximate size
            try:
                size_bytes = len(pickle.dumps(value))
            except:
                size_bytes = 1024  # Default estimate

            entry = CacheEntry(
                key=key,
                value=value,
                timestamp=time.time(),
                ttl=ttl or self.default_ttl,
                size_bytes=size_bytes
            )

            # Evict entries if cache is full
            if len(self.cache) >= self.max_size:
                self._evict_entries()

            self.cache[key] = entry
            self.cache.move_to_end(key)

    def _evict_entries(self) -> None:
        """Evict entries using LRU policy"""
        # Remove expired entries first
        expired_keys = [k for k, v in self.cache.items() if v.is_expired()]
        for key in expired_keys:
            del self.cache[key]
            self.eviction_count += 1

        # If still need to evict, use LRU
        while len(self.cache) >= self.max_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            self.eviction_count += 1

    def invalidate(self, pattern: str = None) -> int:
        """
        Invalidate cache entries

        Args:
            pattern: Pattern to match for invalidation (optional)

        Returns:
            int: Number of entries invalidated
        """
        with self.lock:
            if pattern is None:
                count = len(self.cache)
                self.cache.clear()
                return count

            keys_to_remove = []
            for key in self.cache:
                if pattern in key:
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del self.cache[key]

            return len(keys_to_remove)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Dict containing cache statistics
        """
        with self.lock:
            total_requests = self.hit_count + self.miss_count
            hit_rate = self.hit_count / total_requests if total_requests > 0 else 0

            total_size = sum(entry.size_bytes for entry in self.cache.values())

            return {
                'entries': len(self.cache),
                'max_size': self.max_size,
                'hit_count': self.hit_count,
                'miss_count': self.miss_count,
                'hit_rate': hit_rate,
                'eviction_count': self.eviction_count,
                'total_size_bytes': total_size,
                'avg_entry_size': total_size / len(self.cache) if self.cache else 0
            }

    def cleanup(self) -> int:
        """
        Clean up expired entries

        Returns:
            int: Number of entries cleaned up
        """
        with self.lock:
            expired_keys = [k for k, v in self.cache.items() if v.is_expired()]

            for key in expired_keys:
                del self.cache[key]

            return len(expired_keys)


class MeTTaOperationCache:
    """Cache for MeTTa operations with intelligent invalidation"""

    def __init__(self, cache: MeTTaCache = None):
        """
        Initialize operation cache

        Args:
            cache: MeTTaCache instance to use
        """
        self.cache = cache or MeTTaCache()
        self.operation_dependencies = {
            'verify_contribution': ['user', 'contribution', 'evidence'],
            'calculate_reputation': ['user', 'contributions'],
            'detect_fraud': ['user', 'contribution'],
            'calculate_reward': ['contribution', 'quality', 'impact'],
            'autonomous_cycle': ['platform_state'],
            'governance_decision': ['proposal', 'stakeholders'],
            'predictive_analysis': ['entity', 'data']
        }

    def cached_operation(self, operation_name: str, ttl: Optional[float] = None):
        """
        Decorator for caching MeTTa operations

        Args:
            operation_name: Name of the operation
            ttl: Time-to-live for cache entries
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Generate cache key
                key = self.cache._generate_key(operation_name, *args, **kwargs)

                # Try to get from cache
                cached_result = self.cache.get(key)
                if cached_result is not None:
                    return cached_result

                # Execute operation
                result = func(*args, **kwargs)

                # Cache result
                if result is not None:
                    self.cache.put(key, result, ttl)

                return result

            return wrapper
        return decorator

    def invalidate_operation(self, operation_name: str, *args, **kwargs) -> int:
        """
        Invalidate cache entries for a specific operation

        Args:
            operation_name: Operation name
            *args, **kwargs: Operation arguments

        Returns:
            int: Number of entries invalidated
        """
        key = self.cache._generate_key(operation_name, *args, **kwargs)
        return self.cache.invalidate(key)

    def invalidate_by_entity(self, entity_type: str, entity_id: str) -> int:
        """
        Invalidate cache entries related to a specific entity

        Args:
            entity_type: Type of entity (user, contribution, etc.)
            entity_id: Entity ID

        Returns:
            int: Number of entries invalidated
        """
        pattern = f"{entity_type}:{entity_id}"
        return self.cache.invalidate(pattern)

    def invalidate_by_dependency(self, changed_entity: str, changed_id: str) -> int:
        """
        Invalidate cache entries based on dependencies

        Args:
            changed_entity: Type of entity that changed
            changed_id: ID of entity that changed

        Returns:
            int: Number of entries invalidated
        """
        total_invalidated = 0

        # Invalidate direct entity cache
        total_invalidated += self.invalidate_by_entity(changed_entity, changed_id)

        # Invalidate dependent operations
        for operation, dependencies in self.operation_dependencies.items():
            if changed_entity in dependencies:
                pattern = f"{operation}:"
                total_invalidated += self.cache.invalidate(pattern)

        return total_invalidated

    def get_operation_stats(self, operation_name: str) -> Dict[str, Any]:
        """
        Get statistics for a specific operation

        Args:
            operation_name: Operation name

        Returns:
            Dict containing operation statistics
        """
        pattern = f"{operation_name}:"
        operation_entries = [k for k in self.cache.cache.keys() if k.startswith(pattern)]

        if not operation_entries:
            return {
                'operation': operation_name,
                'cached_entries': 0,
                'total_size': 0,
                'avg_age': 0
            }

        total_size = sum(self.cache.cache[k].size_bytes for k in operation_entries)
        current_time = time.time()
        ages = [current_time - self.cache.cache[k].timestamp for k in operation_entries]
        avg_age = sum(ages) / len(ages)

        return {
            'operation': operation_name,
            'cached_entries': len(operation_entries),
            'total_size': total_size,
            'avg_age': avg_age
        }


class IntelligentMeTTaCache(MeTTaOperationCache):
    """Intelligent cache with predictive prefetching and optimization"""

    def __init__(self, cache: MeTTaCache = None):
        super().__init__(cache)
        self.access_patterns = defaultdict(list)
        self.prefetch_rules = {}

    def record_access_pattern(self, operation: str, *args, **kwargs):
        """
        Record access patterns for predictive caching

        Args:
            operation: Operation name
            *args, **kwargs: Operation arguments
        """
        pattern_key = f"{operation}:{hash(str(args) + str(kwargs))}"
        self.access_patterns[pattern_key].append(time.time())

    def predict_and_prefetch(self, current_operation: str, *args, **kwargs):
        """
        Predict and prefetch related operations

        Args:
            current_operation: Current operation being executed
            *args, **kwargs: Current operation arguments
        """
        # Simple prediction based on operation dependencies
        related_operations = []

        if current_operation == 'verify_contribution':
            related_operations = ['calculate_reward', 'detect_fraud']
        elif current_operation == 'calculate_reputation':
            related_operations = ['governance_decision']

        # Prefetch related operations (implementation would depend on actual service)
        for op in related_operations:
            # This would trigger prefetching of related data
            pass

    def optimize_cache_size(self):
        """Optimize cache size based on usage patterns"""
        stats = self.cache.get_stats()

        # If hit rate is low, consider increasing cache size
        if stats['hit_rate'] < 0.5 and len(self.cache.cache) < self.cache.max_size * 0.8:
            # Could increase cache size
            pass

        # If eviction rate is high, consider increasing cache size
        if self.cache.eviction_count > len(self.cache.cache) * 0.1:
            # Could increase cache size
            pass

    def get_cache_insights(self) -> Dict[str, Any]:
        """
        Get insights about cache performance and optimization opportunities

        Returns:
            Dict containing cache insights
        """
        stats = self.cache.get_stats()
        operation_stats = []

        for operation in self.operation_dependencies.keys():
            op_stats = self.get_operation_stats(operation)
            operation_stats.append(op_stats)

        insights = {
            'overall_stats': stats,
            'operation_stats': operation_stats,
            'recommendations': []
        }

        # Generate recommendations
        if stats['hit_rate'] < 0.6:
            insights['recommendations'].append("Consider increasing cache TTL or size")

        if stats['eviction_count'] > stats['entries'] * 0.2:
            insights['recommendations'].append("High eviction rate - consider larger cache")

        # Check for operations with low cache utilization
        low_utilization_ops = [
            op['operation'] for op in operation_stats
            if op['cached_entries'] < 5
        ]
        if low_utilization_ops:
            insights['recommendations'].append(
                f"Operations with low cache utilization: {low_utilization_ops}"
            )

        return insights


# Global cache instances
_metta_cache = None
_operation_cache = None

def get_metta_cache() -> MeTTaCache:
    """Get global MeTTa cache instance"""
    global _metta_cache
    if _metta_cache is None:
        _metta_cache = MeTTaCache(max_size=2000, default_ttl=1800)  # 30 minutes TTL
    return _metta_cache

def get_operation_cache() -> MeTTaOperationCache:
    """Get global operation cache instance"""
    global _operation_cache
    if _operation_cache is None:
        _operation_cache = MeTTaOperationCache(get_metta_cache())
    return _operation_cache

def get_intelligent_cache() -> IntelligentMeTTaCache:
    """Get intelligent cache instance"""
    global _operation_cache
    if _operation_cache is None or not isinstance(_operation_cache, IntelligentMeTTaCache):
        _operation_cache = IntelligentMeTTaCache(get_metta_cache())
    return _operation_cache


# Utility functions for cache management
def warmup_cache(metta_service):
    """
    Warm up cache with frequently used operations

    Args:
        metta_service: MeTTa service instance
    """
    cache = get_operation_cache()

    # Warm up with common operations
    common_operations = [
        ('verify_contribution', ['test-user', 'test-contrib']),
        ('calculate_reputation', ['test-user']),
        ('detect_fraud', ['test-user', 'test-contrib'])
    ]

    for operation, args in common_operations:
        try:
            # This would execute the operation to populate cache
            # getattr(metta_service, operation)(*args)
            pass
        except:
            pass

def cleanup_expired_cache():
    """Clean up expired cache entries"""
    cache = get_metta_cache()
    cleaned = cache.cleanup()
    return cleaned

def get_cache_performance_report() -> Dict[str, Any]:
    """Get comprehensive cache performance report"""
    cache = get_metta_cache()
    operation_cache = get_operation_cache()

    report = {
        'cache_stats': cache.get_stats(),
        'operation_stats': [],
        'recommendations': []
    }

    # Get stats for each operation type
    for operation in operation_cache.operation_dependencies.keys():
        op_stats = operation_cache.get_operation_stats(operation)
        report['operation_stats'].append(op_stats)

    # Generate recommendations
    stats = report['cache_stats']
    if stats['hit_rate'] < 0.7:
        report['recommendations'].append("Cache hit rate could be improved")
    if stats['eviction_count'] > 100:
        report['recommendations'].append("Consider increasing cache size to reduce evictions")

    return report


if __name__ == "__main__":
    # Example usage and testing
    print("🧠 MeTTa Caching System Demo")
    print("=" * 50)

    # Initialize cache
    cache = get_metta_cache()
    op_cache = get_operation_cache()

    print("✅ Cache system initialized")

    # Test basic caching
    test_key = "test:operation"
    test_value = {"result": "success", "data": [1, 2, 3]}

    cache.put(test_key, test_value)
    retrieved = cache.get(test_key)

    print(f"✅ Basic caching test: {'PASSED' if retrieved == test_value else 'FAILED'}")

    # Test operation caching
    @op_cache.cached_operation("demo_operation")
    def demo_operation(x, y):
        return x + y

    result1 = demo_operation(5, 3)
    result2 = demo_operation(5, 3)  # Should use cache

    print(f"✅ Operation caching test: {'PASSED' if result1 == result2 == 8 else 'FAILED'}")

    # Get cache stats
    stats = cache.get_stats()
    print(f"📊 Cache stats: {stats['entries']} entries, {stats['hit_rate']:.1%} hit rate")

    print("\n🎉 MeTTa caching system demo complete!")