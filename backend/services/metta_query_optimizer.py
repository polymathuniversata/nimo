"""
Optimized MeTTa Query Service

This module provides optimized query execution for MeTTa operations,
including batch processing, query optimization, and connection pooling.
"""

import time
import threading
import logging
from typing import Dict, List, Any, Optional, Union, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import queue

logger = logging.getLogger(__name__)

class QueryOptimizer:
    """Optimizes MeTTa queries for better performance"""

    def __init__(self):
        self.query_cache = {}
        self.query_patterns = defaultdict(int)
        self.optimization_rules = {
            'batch_threshold': 10,  # Batch queries if more than 10
            'cache_ttl': 300,       # Cache results for 5 minutes
            'max_concurrent': 5,    # Max concurrent queries
            'timeout': 30           # Query timeout in seconds
        }

    def optimize_query(self, query_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize a query based on type and parameters"""
        optimized = {
            'original_query': {'type': query_type, 'params': parameters},
            'optimized_params': parameters.copy(),
            'optimization_applied': [],
            'estimated_cost': 1.0
        }

        # Apply query-specific optimizations
        if query_type == 'contribution_validation':
            optimized = self._optimize_contribution_validation(optimized)
        elif query_type == 'user_contributions':
            optimized = self._optimize_user_contributions(optimized)
        elif query_type == 'batch_contributions':
            optimized = self._optimize_batch_contributions(optimized)

        return optimized

    def _optimize_contribution_validation(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize contribution validation queries"""
        params = query['optimized_params']

        # Add optimization flags
        params['use_cache'] = True
        params['simplified_validation'] = True
        query['optimization_applied'].append('cache_enabled')
        query['optimization_applied'].append('simplified_validation')
        query['estimated_cost'] *= 0.7

        return query

    def _optimize_user_contributions(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize user contributions queries"""
        params = query['optimized_params']

        # Add pagination and filtering
        if 'limit' not in params:
            params['limit'] = 50
            query['optimization_applied'].append('default_pagination')

        params['use_index'] = True
        query['optimization_applied'].append('index_usage')
        query['estimated_cost'] *= 0.8

        return query

    def _optimize_batch_contributions(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize batch contribution queries"""
        params = query['optimized_params']

        # Enable batch processing optimizations
        params['batch_size'] = min(params.get('batch_size', 20), 50)
        params['parallel_processing'] = True
        params['use_cache'] = True

        query['optimization_applied'].extend([
            'batch_processing',
            'parallel_execution',
            'cache_enabled'
        ])
        query['estimated_cost'] *= 0.5

        return query

class BatchProcessor:
    """Handles batch processing of MeTTa operations"""

    def __init__(self, max_workers: int = 5, batch_size: int = 20):
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.query_optimizer = QueryOptimizer()

    def process_batch(self, operation_type: str, items: List[Any],
                     operation_func: Callable, **kwargs) -> Dict[str, Any]:
        """Process a batch of items with the given operation"""
        if not items:
            return {'results': [], 'success_count': 0, 'error_count': 0}

        # Split into batches
        batches = [items[i:i + self.batch_size] for i in range(0, len(items), self.batch_size)]

        results = []
        success_count = 0
        error_count = 0

        # Submit batches for parallel processing
        future_to_batch = {
            self.executor.submit(self._process_single_batch, operation_type, batch, operation_func, kwargs): batch
            for batch in batches
        }

        # Collect results
        for future in as_completed(future_to_batch):
            batch = future_to_batch[future]
            try:
                batch_result = future.result(timeout=60)
                results.extend(batch_result['results'])
                success_count += batch_result['success_count']
                error_count += batch_result['error_count']
            except Exception as e:
                logger.error(f"Batch processing failed for batch of {len(batch)} items: {e}")
                error_count += len(batch)

        return {
            'results': results,
            'success_count': success_count,
            'error_count': error_count,
            'total_processed': len(items),
            'batch_count': len(batches)
        }

    def _process_single_batch(self, operation_type: str, batch: List[Any],
                            operation_func: Callable, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single batch of items"""
        results = []
        success_count = 0
        error_count = 0

        for item in batch:
            try:
                # Optimize the query for this item
                optimized_query = self.query_optimizer.optimize_query(operation_type, {'item': item, **kwargs})

                # Execute the operation
                result = operation_func(item, **optimized_query['optimized_params'])

                results.append({
                    'item': item,
                    'result': result,
                    'success': True,
                    'optimizations': optimized_query['optimization_applied']
                })
                success_count += 1

            except Exception as e:
                logger.error(f"Failed to process item {item}: {e}")
                results.append({
                    'item': item,
                    'error': str(e),
                    'success': False
                })
                error_count += 1

        return {
            'results': results,
            'success_count': success_count,
            'error_count': error_count
        }

class ConnectionPool:
    """Manages connection pooling for MeTTa operations"""

    def __init__(self, max_connections: int = 10, connection_timeout: int = 30):
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        self.connections = queue.Queue(maxsize=max_connections)
        self.active_connections = 0
        self.lock = threading.Lock()

        # Initialize connection pool
        self._initialize_pool()

    def _initialize_pool(self):
        """Initialize the connection pool"""
        for _ in range(self.max_connections):
            self.connections.put(self._create_connection())

    def _create_connection(self) -> Dict[str, Any]:
        """Create a new connection (placeholder for actual MeTTa connection)"""
        return {
            'id': f"conn_{int(time.time() * 1000)}",
            'created_at': time.time(),
            'last_used': time.time(),
            'status': 'available'
        }

    def get_connection(self) -> Optional[Dict[str, Any]]:
        """Get a connection from the pool"""
        try:
            with self.lock:
                connection = self.connections.get(timeout=self.connection_timeout)
                connection['last_used'] = time.time()
                connection['status'] = 'active'
                self.active_connections += 1
                return connection
        except queue.Empty:
            logger.warning("Connection pool exhausted")
            return None

    def return_connection(self, connection: Dict[str, Any]):
        """Return a connection to the pool"""
        if connection:
            with self.lock:
                connection['status'] = 'available'
                connection['last_used'] = time.time()
                self.connections.put(connection)
                self.active_connections -= 1

    def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        with self.lock:
            return {
                'max_connections': self.max_connections,
                'active_connections': self.active_connections,
                'available_connections': self.connections.qsize(),
                'pool_utilization': self.active_connections / self.max_connections
            }

class OptimizedMeTTaQueryService:
    """Optimized MeTTa query service with batch processing and connection pooling"""

    def __init__(self, max_workers: int = 5, max_connections: int = 10):
        self.batch_processor = BatchProcessor(max_workers=max_workers)
        self.connection_pool = ConnectionPool(max_connections=max_connections)
        self.query_optimizer = QueryOptimizer()

        # Performance tracking
        self.query_stats = defaultdict(lambda: {
            'total_queries': 0,
            'successful_queries': 0,
            'failed_queries': 0,
            'avg_duration': 0.0,
            'total_duration': 0.0
        })

        logger.info("Optimized MeTTa Query Service initialized")

    def execute_optimized_query(self, query_type: str, parameters: Dict[str, Any],
                              query_func: Callable) -> Any:
        """Execute an optimized query"""
        start_time = time.time()

        try:
            # Optimize the query
            optimized_query = self.query_optimizer.optimize_query(query_type, parameters)

            # Get connection from pool
            connection = self.connection_pool.get_connection()
            if not connection:
                raise RuntimeError("No available connections in pool")

            try:
                # Execute the query
                result = query_func(**optimized_query['optimized_params'])

                # Update stats
                self._update_query_stats(query_type, time.time() - start_time, True)

                return {
                    'result': result,
                    'optimizations_applied': optimized_query['optimization_applied'],
                    'estimated_cost': optimized_query['estimated_cost'],
                    'execution_time': time.time() - start_time
                }

            finally:
                # Return connection to pool
                self.connection_pool.return_connection(connection)

        except Exception as e:
            # Update stats for failed query
            self._update_query_stats(query_type, time.time() - start_time, False)
            logger.error(f"Optimized query failed: {e}")
            raise

    def execute_batch_query(self, query_type: str, items: List[Any],
                          operation_func: Callable, **kwargs) -> Dict[str, Any]:
        """Execute a batch query with optimizations"""
        start_time = time.time()

        try:
            # Process batch
            batch_result = self.batch_processor.process_batch(
                query_type, items, operation_func, **kwargs
            )

            # Update stats
            total_time = time.time() - start_time
            self._update_batch_stats(query_type, len(items), batch_result['success_count'],
                                   batch_result['error_count'], total_time)

            return {
                **batch_result,
                'total_execution_time': total_time,
                'avg_time_per_item': total_time / len(items) if items else 0
            }

        except Exception as e:
            logger.error(f"Batch query failed: {e}")
            raise

    def _update_query_stats(self, query_type: str, duration: float, success: bool):
        """Update query statistics"""
        stats = self.query_stats[query_type]
        stats['total_queries'] += 1

        if success:
            stats['successful_queries'] += 1
        else:
            stats['failed_queries'] += 1

        # Update average duration
        stats['total_duration'] += duration
        stats['avg_duration'] = stats['total_duration'] / stats['total_queries']

    def _update_batch_stats(self, query_type: str, total_items: int,
                          success_count: int, error_count: int, duration: float):
        """Update batch query statistics"""
        # Update individual query stats for each item
        for _ in range(total_items):
            self._update_query_stats(f"{query_type}_batch_item", duration / total_items,
                                   success_count > error_count)

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        total_queries = sum(stats['total_queries'] for stats in self.query_stats.values())
        successful_queries = sum(stats['successful_queries'] for stats in self.query_stats.values())

        return {
            'query_stats': dict(self.query_stats),
            'connection_pool_stats': self.connection_pool.get_pool_stats(),
            'overall_stats': {
                'total_queries': total_queries,
                'successful_queries': successful_queries,
                'success_rate': successful_queries / total_queries if total_queries > 0 else 0,
                'query_types_count': len(self.query_stats)
            }
        }

    def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        pool_stats = self.connection_pool.get_pool_stats()

        health_status = {
            'status': 'healthy',
            'connection_pool': {
                'healthy': pool_stats['available_connections'] > 0,
                'utilization': pool_stats['pool_utilization']
            },
            'batch_processor': {
                'healthy': True,
                'max_workers': self.batch_processor.max_workers
            },
            'query_optimizer': {
                'healthy': True
            }
        }

        # Determine overall health
        if pool_stats['pool_utilization'] > 0.9:
            health_status['status'] = 'warning'
            health_status['message'] = 'High connection pool utilization'

        if pool_stats['available_connections'] == 0:
            health_status['status'] = 'critical'
            health_status['message'] = 'No available connections'

        return health_status

# Global instance
_optimized_query_service = None

def get_optimized_query_service() -> OptimizedMeTTaQueryService:
    """Get the global optimized query service instance"""
    global _optimized_query_service

    if _optimized_query_service is None:
        _optimized_query_service = OptimizedMeTTaQueryService()

    return _optimized_query_service

def reset_optimized_query_service():
    """Reset the global query service instance"""
    global _optimized_query_service
    _optimized_query_service = None

# Convenience functions
def execute_optimized_query(query_type: str, parameters: Dict[str, Any], query_func: Callable) -> Any:
    """Execute an optimized query"""
    return get_optimized_query_service().execute_optimized_query(query_type, parameters, query_func)

def execute_batch_query(query_type: str, items: List[Any], operation_func: Callable, **kwargs) -> Dict[str, Any]:
    """Execute a batch query"""
    return get_optimized_query_service().execute_batch_query(query_type, items, operation_func, **kwargs)

if __name__ == "__main__":
    # Test the optimized query service
    service = OptimizedMeTTaQueryService()

    # Test query optimization
    optimized = service.query_optimizer.optimize_query('contribution_validation', {'contribution_id': 'test_123'})
    print("Query optimization test:", optimized)

    # Test connection pool
    conn = service.connection_pool.get_connection()
    print("Connection pool test:", conn is not None)

    if conn:
        service.connection_pool.return_connection(conn)

    # Test health check
    health = service.health_check()
    print("Health check:", health)