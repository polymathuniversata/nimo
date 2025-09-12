"""
Performance Monitoring Service for MeTTa Autonomous System

This module provides comprehensive performance monitoring and metrics
collection for autonomous operations, MeTTa queries, and system health.
"""

import time
import threading
import psutil
import statistics
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Performance monitoring service for autonomous operations"""

    def __init__(self, max_metrics_history: int = 1000):
        """
        Initialize performance monitor

        Args:
            max_metrics_history: Maximum number of metrics to keep in history
        """
        self.max_metrics_history = max_metrics_history
        self.metrics_history = defaultdict(lambda: deque(maxlen=max_metrics_history))
        self.active_operations = {}
        self.operation_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
        self.start_time = time.time()

        # Thread safety
        self.lock = threading.Lock()

        # System metrics
        self.system_metrics = {
            'cpu_percent': [],
            'memory_percent': [],
            'disk_usage': [],
            'network_io': []
        }

        # Start background monitoring
        self.monitoring_thread = threading.Thread(target=self._background_monitor, daemon=True)
        self.monitoring_thread.start()

    def monitor_operation(self, operation_name: str):
        """Context manager for monitoring operation performance"""
        return OperationMonitor(self, operation_name)

    def record_operation_start(self, operation_name: str, operation_id: Optional[str] = None) -> str:
        """Record the start of an operation"""
        if operation_id is None:
            operation_id = f"{operation_name}_{int(time.time() * 1000)}"

        with self.lock:
            self.active_operations[operation_id] = {
                'operation': operation_name,
                'start_time': time.time(),
                'status': 'running'
            }

        return operation_id

    def record_operation_end(self, operation_id: str, success: bool = True,
                           metadata: Optional[Dict[str, Any]] = None):
        """Record the end of an operation"""
        with self.lock:
            if operation_id in self.active_operations:
                operation = self.active_operations[operation_id]
                end_time = time.time()
                duration = end_time - operation['start_time']

                # Record metrics
                operation_name = operation['operation']
                self._record_metric(operation_name, 'duration', duration)
                self._record_metric(operation_name, 'success_rate', 1.0 if success else 0.0)

                if not success:
                    self.error_counts[operation_name] += 1

                self.operation_counts[operation_name] += 1

                # Update operation status
                operation.update({
                    'end_time': end_time,
                    'duration': duration,
                    'success': success,
                    'status': 'completed' if success else 'failed',
                    'metadata': metadata or {}
                })

                # Keep completed operations for a short time
                threading.Timer(300, lambda: self.active_operations.pop(operation_id, None)).start()

    def _record_metric(self, operation: str, metric_name: str, value: float):
        """Record a metric value"""
        metric_key = f"{operation}.{metric_name}"
        self.metrics_history[metric_key].append({
            'value': value,
            'timestamp': time.time()
        })

    def get_operation_stats(self, operation_name: str, time_window: int = 3600) -> Dict[str, Any]:
        """Get statistics for a specific operation"""
        current_time = time.time()
        cutoff_time = current_time - time_window

        with self.lock:
            # Filter metrics by time window
            duration_metrics = []
            success_metrics = []

            for metric in self.metrics_history[f"{operation_name}.duration"]:
                if metric['timestamp'] > cutoff_time:
                    duration_metrics.append(metric['value'])

            for metric in self.metrics_history[f"{operation_name}.success_rate"]:
                if metric['timestamp'] > cutoff_time:
                    success_metrics.append(metric['value'])

            # Calculate statistics
            stats = {
                'operation': operation_name,
                'total_operations': self.operation_counts[operation_name],
                'error_count': self.error_counts[operation_name],
                'time_window_seconds': time_window
            }

            if duration_metrics:
                stats.update({
                    'avg_duration': statistics.mean(duration_metrics),
                    'min_duration': min(duration_metrics),
                    'max_duration': max(duration_metrics),
                    'p95_duration': statistics.quantiles(duration_metrics, n=20)[18] if len(duration_metrics) >= 20 else max(duration_metrics),
                    'duration_count': len(duration_metrics)
                })

            if success_metrics:
                stats.update({
                    'success_rate': statistics.mean(success_metrics),
                    'success_count': len(success_metrics)
                })

            return stats

    def get_system_health(self) -> Dict[str, Any]:
        """Get current system health metrics"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'uptime_seconds': time.time() - self.start_time,
                'active_operations': len(self.active_operations),
                'total_operations': sum(self.operation_counts.values()),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.warning(f"Failed to get system health: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def get_all_operation_stats(self, time_window: int = 3600) -> Dict[str, Any]:
        """Get statistics for all operations"""
        operations = set()
        with self.lock:
            for key in self.metrics_history.keys():
                if '.' in key:
                    operations.add(key.split('.')[0])

        stats = {}
        for operation in operations:
            stats[operation] = self.get_operation_stats(operation, time_window)

        return {
            'operations': stats,
            'summary': {
                'total_operations': sum(self.operation_counts.values()),
                'total_errors': sum(self.error_counts.values()),
                'active_operations': len(self.active_operations),
                'time_window_seconds': time_window,
                'generated_at': datetime.now().isoformat()
            }
        }

    def get_performance_report(self, time_window: int = 3600) -> Dict[str, Any]:
        """Generate a comprehensive performance report"""
        operation_stats = self.get_all_operation_stats(time_window)
        system_health = self.get_system_health()

        # Identify bottlenecks
        bottlenecks = []
        for operation, stats in operation_stats['operations'].items():
            if 'avg_duration' in stats and stats['avg_duration'] > 5.0:  # 5 second threshold
                bottlenecks.append({
                    'operation': operation,
                    'avg_duration': stats['avg_duration'],
                    'severity': 'high' if stats['avg_duration'] > 10.0 else 'medium'
                })

        # Performance recommendations
        recommendations = []
        if system_health.get('cpu_percent', 0) > 80:
            recommendations.append("High CPU usage detected - consider optimizing compute-intensive operations")
        if system_health.get('memory_percent', 0) > 85:
            recommendations.append("High memory usage detected - consider implementing memory optimization")
        if bottlenecks:
            recommendations.append(f"Performance bottlenecks detected in {len(bottlenecks)} operations")

        return {
            'time_window_seconds': time_window,
            'generated_at': datetime.now().isoformat(),
            'system_health': system_health,
            'operation_stats': operation_stats,
            'bottlenecks': bottlenecks,
            'recommendations': recommendations
        }

    def _background_monitor(self):
        """Background monitoring thread"""
        while True:
            try:
                # Collect system metrics every 30 seconds
                time.sleep(30)

                try:
                    cpu_percent = psutil.cpu_percent(interval=0.1)
                    memory_percent = psutil.virtual_memory().percent
                    disk_usage = psutil.disk_usage('/').percent

                    with self.lock:
                        self.system_metrics['cpu_percent'].append(cpu_percent)
                        self.system_metrics['memory_percent'].append(memory_percent)
                        self.system_metrics['disk_usage'].append(disk_usage)

                        # Keep only last 100 readings
                        for metric_list in self.system_metrics.values():
                            if len(metric_list) > 100:
                                metric_list.pop(0)

                except Exception as e:
                    logger.warning(f"Background monitoring error: {e}")

            except Exception as e:
                logger.error(f"Background monitoring thread error: {e}")
                time.sleep(60)  # Wait before retrying

    def cleanup_old_data(self, max_age_seconds: int = 86400):  # 24 hours
        """Clean up old metrics data"""
        cutoff_time = time.time() - max_age_seconds

        with self.lock:
            for metric_key, metrics in self.metrics_history.items():
                # Remove old metrics
                while metrics and metrics[0]['timestamp'] < cutoff_time:
                    metrics.popleft()

    def export_metrics(self, format: str = 'json') -> str:
        """Export metrics in specified format"""
        data = {
            'exported_at': datetime.now().isoformat(),
            'system_health': self.get_system_health(),
            'operation_stats': self.get_all_operation_stats(),
            'active_operations': dict(self.active_operations),
            'operation_counts': dict(self.operation_counts),
            'error_counts': dict(self.error_counts)
        }

        if format == 'json':
            import json
            return json.dumps(data, indent=2, default=str)
        else:
            return str(data)

class OperationMonitor:
    """Context manager for monitoring operations"""

    def __init__(self, monitor: PerformanceMonitor, operation_name: str):
        self.monitor = monitor
        self.operation_name = operation_name
        self.operation_id = None
        self.metadata = {}

    def __enter__(self):
        self.operation_id = self.monitor.record_operation_start(self.operation_name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        success = exc_type is None
        if exc_val:
            self.metadata['error'] = str(exc_val)

        self.monitor.record_operation_end(self.operation_id, success, self.metadata)

    def add_metadata(self, key: str, value: Any):
        """Add metadata to the operation"""
        self.metadata[key] = value

# Global monitor instance
_monitor_instance = None
_monitor_lock = threading.Lock()

def get_monitor() -> PerformanceMonitor:
    """Get or create global monitor instance"""
    global _monitor_instance

    if _monitor_instance is None:
        with _monitor_lock:
            if _monitor_instance is None:
                _monitor_instance = PerformanceMonitor()

    return _monitor_instance

def monitor_operation(operation_name: str):
    """Decorator for monitoring function performance"""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            monitor = get_monitor()
            with monitor.monitor_operation(operation_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator

# Convenience functions
def record_operation_start(operation_name: str, operation_id: Optional[str] = None) -> str:
    """Record operation start"""
    return get_monitor().record_operation_start(operation_name, operation_id)

def record_operation_end(operation_id: str, success: bool = True, metadata: Optional[Dict[str, Any]] = None):
    """Record operation end"""
    get_monitor().record_operation_end(operation_id, success, metadata)

def get_performance_report(time_window: int = 3600) -> Dict[str, Any]:
    """Get performance report"""
    return get_monitor().get_performance_report(time_window)

if __name__ == "__main__":
    # Test the performance monitor
    monitor = PerformanceMonitor()

    # Simulate some operations
    with monitor.monitor_operation("test_operation") as op_monitor:
        time.sleep(0.1)
        op_monitor.add_metadata("test_data", "sample")

    # Get stats
    stats = monitor.get_operation_stats("test_operation")
    print("Operation stats:", stats)

    # Get system health
    health = monitor.get_system_health()
    print("System health:", health)

    # Get performance report
    report = monitor.get_performance_report()
    print("Performance report generated")