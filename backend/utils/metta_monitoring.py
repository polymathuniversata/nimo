"""
MeTTa Autonomous System Monitoring & Logging

This module provides comprehensive monitoring, logging, and alerting
for the MeTTa autonomous system operations.
"""

import logging
import time
import json
import threading
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import psutil
import os
from functools import wraps


@dataclass
class OperationMetrics:
    """Metrics for a single operation"""
    operation_name: str
    call_count: int = 0
    total_time: float = 0.0
    avg_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    error_count: int = 0
    success_count: int = 0
    last_called: Optional[float] = None
    timestamps: List[float] = field(default_factory=list)

    def record_call(self, duration: float, success: bool = True):
        """Record a call to this operation"""
        self.call_count += 1
        self.total_time += duration
        self.avg_time = self.total_time / self.call_count
        self.min_time = min(self.min_time, duration)
        self.max_time = max(self.max_time, duration)
        self.last_called = time.time()

        if success:
            self.success_count += 1
        else:
            self.error_count += 1

        # Keep only recent timestamps (last 1000)
        self.timestamps.append(time.time())
        if len(self.timestamps) > 1000:
            self.timestamps.pop(0)

    def get_success_rate(self) -> float:
        """Get success rate as percentage"""
        if self.call_count == 0:
            return 0.0
        return (self.success_count / self.call_count) * 100

    def get_calls_per_minute(self) -> float:
        """Get average calls per minute over last hour"""
        if len(self.timestamps) < 2:
            return 0.0

        # Calculate calls in last hour
        one_hour_ago = time.time() - 3600
        recent_calls = [t for t in self.timestamps if t > one_hour_ago]

        if not recent_calls:
            return 0.0

        time_span = time.time() - recent_calls[0]
        if time_span == 0:
            return 0.0

        return len(recent_calls) / (time_span / 60)


@dataclass
class SystemHealth:
    """System health metrics"""
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    network_connections: int = 0
    thread_count: int = 0
    uptime: float = 0.0
    timestamp: float = field(default_factory=time.time)

    def update(self):
        """Update system health metrics"""
        self.cpu_usage = psutil.cpu_percent(interval=1)
        self.memory_usage = psutil.virtual_memory().percent
        self.disk_usage = psutil.disk_usage('/').percent
        self.network_connections = len(psutil.net_connections())
        self.thread_count = threading.active_count()
        self.uptime = time.time() - psutil.boot_time()
        self.timestamp = time.time()


class MeTTaMonitor:
    """Comprehensive monitoring system for MeTTa operations"""

    def __init__(self, log_file: str = "metta_monitor.log"):
        """
        Initialize MeTTa monitor

        Args:
            log_file: Path to log file
        """
        self.metrics: Dict[str, OperationMetrics] = {}
        self.health = SystemHealth()
        self.alerts: List[Dict[str, Any]] = []
        self.alert_callbacks: List[Callable] = []

        # Setup logging
        self.logger = logging.getLogger('MeTTaMonitor')
        self.logger.setLevel(logging.INFO)

        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # Start health monitoring thread
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._health_monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def monitor_operation(self, operation_name_or_func=None):
        """
        Decorator/context manager to monitor an operation

        Args:
            operation_name_or_func: Either operation name (str) for context manager,
                                   function for decorator, or None for decorator without parens

        Returns:
            Context manager or decorated function
        """
        # If called without arguments, return decorator
        if operation_name_or_func is None:
            return lambda func: self._monitor_operation_context(func.__name__, func)

        # If it's a string, return a context manager
        if isinstance(operation_name_or_func, str):
            return self.OperationContext(self, operation_name_or_func)

        # If it's a function, return a decorated function
        func = operation_name_or_func

        @wraps(func)
        def wrapper(*args, **kwargs):
            return self._monitor_operation_context(func.__name__, func, *args, **kwargs)

        return wrapper

    class OperationContext:
        """Context manager for operation monitoring"""

        def __init__(self, monitor, operation_name: str):
            self.monitor = monitor
            self.operation_name = operation_name
            self.start_time = None

        def __enter__(self):
            self.start_time = time.time()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            duration = time.time() - self.start_time

            if self.operation_name not in self.monitor.metrics:
                self.monitor.metrics[self.operation_name] = OperationMetrics(self.operation_name)

            success = exc_type is None
            self.monitor.metrics[self.operation_name].record_call(duration, success=success)

            if success:
                self.monitor.logger.info(
                    f"Operation '{self.operation_name}' completed successfully in {duration:.3f}s"
                )
            else:
                self.monitor.logger.error(
                    f"Operation '{self.operation_name}' failed after {duration:.3f}s: {str(exc_val) if exc_val else 'Unknown error'}"
                )
                self.monitor._check_alerts(self.operation_name)

    def _health_monitor_loop(self):
        """Background thread for health monitoring"""
        while self.monitoring_active:
            try:
                self.health.update()

                # Check for health alerts
                self._check_health_alerts()

                # Log health status periodically
                if int(time.time()) % 300 == 0:  # Every 5 minutes
                    self._log_health_status()

                time.sleep(60)  # Update every minute

            except Exception as e:
                self.logger.error(f"Health monitoring error: {str(e)}")
                time.sleep(60)

    def _check_health_alerts(self):
        """Check for health-related alerts"""
        alerts = []

        if self.health.cpu_usage > 90:
            alerts.append({
                'type': 'high_cpu',
                'message': f'CPU usage is {self.health.cpu_usage:.1f}%',
                'severity': 'critical',
                'timestamp': time.time()
            })

        if self.health.memory_usage > 90:
            alerts.append({
                'type': 'high_memory',
                'message': f'Memory usage is {self.health.memory_usage:.1f}%',
                'severity': 'critical',
                'timestamp': time.time()
            })

        if self.health.disk_usage > 95:
            alerts.append({
                'type': 'low_disk_space',
                'message': f'Disk usage is {self.health.disk_usage:.1f}%',
                'severity': 'warning',
                'timestamp': time.time()
            })

        for alert in alerts:
            self.alerts.append(alert)
            self.logger.warning(f"Health alert: {alert['message']}")
            self._trigger_alert_callbacks(alert)

    def _check_alerts(self, operation_name: str):
        """Check for operation-specific alerts"""
        if operation_name not in self.metrics:
            return

        metrics = self.metrics[operation_name]
        alerts = []

        # Check error rate
        error_rate = (metrics.error_count / metrics.call_count) * 100 if metrics.call_count > 0 else 0
        if error_rate > 20:  # More than 20% errors
            alerts.append({
                'type': 'high_error_rate',
                'operation': operation_name,
                'message': f'High error rate for {operation_name}: {error_rate:.1f}%',
                'severity': 'warning',
                'timestamp': time.time()
            })

        # Check performance degradation
        if metrics.avg_time > 10:  # Operations taking more than 10 seconds
            alerts.append({
                'type': 'slow_operation',
                'operation': operation_name,
                'message': f'Slow operation {operation_name}: {metrics.avg_time:.3f}s average',
                'severity': 'warning',
                'timestamp': time.time()
            })

        for alert in alerts:
            self.alerts.append(alert)
            self.logger.warning(f"Operation alert: {alert['message']}")
            self._trigger_alert_callbacks(alert)

    def _trigger_alert_callbacks(self, alert: Dict[str, Any]):
        """Trigger alert callbacks"""
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Alert callback error: {str(e)}")

    def _monitor_operation_context(self, operation_name: str, func, *args, **kwargs):
        """
        Internal method to handle operation monitoring with timing

        Args:
            operation_name: Name of the operation
            func: Function to execute
            *args, **kwargs: Function arguments

        Returns:
            Function result
        """
        start_time = time.time()

        if operation_name not in self.metrics:
            self.metrics[operation_name] = OperationMetrics(operation_name)

        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            self.metrics[operation_name].record_call(duration, success=True)
            self.logger.info(
                f"Operation '{operation_name}' completed successfully in {duration:.3f}s"
            )
            return result

        except Exception as e:
            duration = time.time() - start_time
            self.metrics[operation_name].record_call(duration, success=False)
            self.logger.error(
                f"Operation '{operation_name}' failed after {duration:.3f}s: {str(e)}"
            )
            self._check_alerts(operation_name)
            raise

    def add_alert_callback(self, callback: Callable):
        """
        Add a callback for alerts

        Args:
            callback: Function to call when alerts are triggered
        """
        self.alert_callbacks.append(callback)

    def _log_health_status(self):
        """Log current health status"""
        self.logger.info(
            f"Health status - CPU: {self.health.cpu_usage:.1f}%, "
            f"Memory: {self.health.memory_usage:.1f}%, "
            f"Disk: {self.health.disk_usage:.1f}%, "
            f"Threads: {self.health.thread_count}"
        )

    def get_operation_report(self, operation_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get operation performance report

        Args:
            operation_name: Specific operation to report on (optional)

        Returns:
            Dict containing operation metrics
        """
        if operation_name:
            if operation_name not in self.metrics:
                return {'error': f'Operation {operation_name} not found'}

            metrics = self.metrics[operation_name]
            return {
                'operation': operation_name,
                'call_count': metrics.call_count,
                'avg_time': metrics.avg_time,
                'min_time': metrics.min_time,
                'max_time': metrics.max_time,
                'success_rate': metrics.get_success_rate(),
                'calls_per_minute': metrics.get_calls_per_minute(),
                'error_count': metrics.error_count,
                'last_called': metrics.last_called
            }

        # Summary report for all operations
        operations = []
        total_calls = 0
        total_errors = 0

        for name, metrics in self.metrics.items():
            operations.append({
                'name': name,
                'calls': metrics.call_count,
                'avg_time': metrics.avg_time,
                'success_rate': metrics.get_success_rate(),
                'errors': metrics.error_count
            })
            total_calls += metrics.call_count
            total_errors += metrics.error_count

        return {
            'total_operations': len(self.metrics),
            'total_calls': total_calls,
            'total_errors': total_errors,
            'overall_success_rate': ((total_calls - total_errors) / total_calls * 100) if total_calls > 0 else 0,
            'operations': operations
        }

    def get_health_report(self) -> Dict[str, Any]:
        """
        Get system health report

        Returns:
            Dict containing health metrics
        """
        return {
            'cpu_usage': self.health.cpu_usage,
            'memory_usage': self.health.memory_usage,
            'disk_usage': self.health.disk_usage,
            'network_connections': self.health.network_connections,
            'thread_count': self.health.thread_count,
            'uptime_hours': self.health.uptime / 3600,
            'timestamp': self.health.timestamp
        }

    def get_alert_report(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get alerts from the last N hours

        Args:
            hours: Number of hours to look back

        Returns:
            List of recent alerts
        """
        cutoff_time = time.time() - (hours * 3600)
        recent_alerts = [alert for alert in self.alerts if alert['timestamp'] > cutoff_time]

        return recent_alerts

    def export_metrics(self, filepath: str):
        """
        Export all metrics to a JSON file

        Args:
            filepath: Path to export file
        """
        export_data = {
            'timestamp': time.time(),
            'health': self.get_health_report(),
            'operations': self.get_operation_report(),
            'alerts': self.get_alert_report(hours=168)  # Last 7 days
        }

        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)

        self.logger.info(f"Metrics exported to {filepath}")

    def shutdown(self):
        """Shutdown the monitoring system"""
        self.monitoring_active = False
        if self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)

        self.logger.info("MeTTa monitoring system shut down")


class MeTTaLogger:
    """Enhanced logging system for MeTTa operations"""

    def __init__(self, base_log_dir: str = "logs"):
        """
        Initialize MeTTa logger

        Args:
            base_log_dir: Base directory for log files
        """
        self.base_log_dir = base_log_dir
        os.makedirs(base_log_dir, exist_ok=True)

        # Setup different loggers for different components
        self.setup_component_loggers()

    def setup_component_loggers(self):
        """Setup loggers for different MeTTa components"""
        components = [
            'metta_reasoning',
            'metta_integration',
            'autonomous_system',
            'cache_system',
            'performance_optimizer'
        ]

        self.loggers = {}

        for component in components:
            logger = logging.getLogger(f'MeTTa.{component}')
            logger.setLevel(logging.INFO)

            # Create log file for this component
            log_file = os.path.join(self.base_log_dir, f'{component}.log')

            # File handler
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)

            # Formatter with more detail
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
            )
            file_handler.setFormatter(formatter)

            # Clear existing handlers to avoid duplicates
            logger.handlers.clear()
            logger.addHandler(file_handler)

            self.loggers[component] = logger

    def get_logger(self, component: str) -> logging.Logger:
        """
        Get logger for a specific component

        Args:
            component: Component name

        Returns:
            Logger instance
        """
        return self.loggers.get(component, logging.getLogger('MeTTa.default'))

    def log_operation_start(self, component: str, operation: str, *args, **kwargs):
        """
        Log the start of an operation

        Args:
            component: Component name
            operation: Operation name
            *args, **kwargs: Operation arguments
        """
        logger = self.get_logger(component)
        logger.info(f"Starting operation: {operation}")

        if args or kwargs:
            # Log arguments (be careful with sensitive data)
            safe_args = [str(arg) for arg in args]
            safe_kwargs = {k: str(v) for k, v in kwargs.items()}
            logger.debug(f"Operation args: {safe_args}, kwargs: {safe_kwargs}")

    def log_operation_end(self, component: str, operation: str, duration: float, success: bool = True, result=None):
        """
        Log the end of an operation

        Args:
            component: Component name
            operation: Operation name
            duration: Operation duration in seconds
            success: Whether operation was successful
            result: Operation result (optional)
        """
        logger = self.get_logger(component)
        status = "SUCCESS" if success else "FAILED"

        logger.info(f"Operation {operation} completed in {duration:.3f}s - {status}")

        if result is not None and success:
            # Log result summary (avoid logging large objects)
            if isinstance(result, (dict, list)):
                result_summary = f"Result type: {type(result).__name__}, length: {len(result)}"
            else:
                result_summary = str(result)[:100]  # Truncate long results

            logger.debug(f"Operation result: {result_summary}")

    def log_error(self, component: str, operation: str, error: Exception, context: Dict[str, Any] = None):
        """
        Log an error with context

        Args:
            component: Component name
            operation: Operation name
            error: Exception that occurred
            context: Additional context information
        """
        logger = self.get_logger(component)

        logger.error(f"Error in {operation}: {str(error)}")

        if context:
            logger.error(f"Error context: {json.dumps(context, default=str)}")

        # Log full traceback
        logger.exception("Full error traceback:")

    def log_performance_metric(self, component: str, metric_name: str, value: float, unit: str = ""):
        """
        Log a performance metric

        Args:
            component: Component name
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement
        """
        logger = self.get_logger(component)
        unit_str = f" {unit}" if unit else ""
        logger.info(f"Performance metric - {metric_name}: {value:.3f}{unit_str}")

    def log_cache_event(self, component: str, event_type: str, key: str, details: Dict[str, Any] = None):
        """
        Log cache-related events

        Args:
            component: Component name
            event_type: Type of cache event (hit, miss, eviction, etc.)
            key: Cache key
            details: Additional event details
        """
        logger = self.get_logger(component)

        message = f"Cache {event_type}: {key}"
        if details:
            message += f" - {json.dumps(details, default=str)}"

        logger.info(message)

    def rotate_logs(self, max_age_days: int = 30):
        """
        Rotate old log files

        Args:
            max_age_days: Maximum age of log files in days
        """
        cutoff_time = time.time() - (max_age_days * 24 * 3600)

        for filename in os.listdir(self.base_log_dir):
            if filename.endswith('.log'):
                filepath = os.path.join(self.base_log_dir, filename)
                if os.path.getmtime(filepath) < cutoff_time:
                    os.remove(filepath)
                    print(f"Removed old log file: {filename}")


# Global instances
_monitor = None
_logger = None

def get_monitor() -> MeTTaMonitor:
    """Get global monitor instance"""
    global _monitor
    if _monitor is None:
        _monitor = MeTTaMonitor()
    return _monitor

def get_logger() -> MeTTaLogger:
    """Get global logger instance"""
    global _logger
    if _logger is None:
        _logger = MeTTaLogger()
    return _logger

def log_operation(component: str, operation: str):
    """
    Decorator to log operations with timing

    Args:
        component: Component name
        operation: Operation name
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger()
            monitor = get_monitor()

            # Log operation start
            logger.log_operation_start(component, operation, *args, **kwargs)

            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                # Log operation end
                logger.log_operation_end(component, operation, duration, success=True, result=result)

                # Monitor the operation
                monitor.metrics[operation].record_call(duration, success=True)

                return result

            except Exception as e:
                duration = time.time() - start_time

                # Log error
                logger.log_error(component, operation, e, {'args': args, 'kwargs': kwargs})

                # Monitor the error
                monitor.metrics[operation].record_call(duration, success=False)

                raise

        return wrapper
    return decorator


if __name__ == "__main__":
    # Example usage and testing
    print("📊 MeTTa Monitoring & Logging System Demo")
    print("=" * 50)

    # Initialize systems
    monitor = get_monitor()
    logger = get_logger()

    print("✅ Monitoring and logging systems initialized")

    # Test operation monitoring
    @monitor.monitor_operation("demo_operation")
    @log_operation("demo_component", "demo_operation")
    def demo_operation(x, y):
        time.sleep(0.1)  # Simulate work
        return x + y

    # Test the monitored operation
    try:
        result = demo_operation(5, 3)
        print(f"✅ Monitored operation result: {result}")
    except Exception as e:
        print(f"❌ Operation failed: {e}")

    # Get reports
    op_report = monitor.get_operation_report()
    health_report = monitor.get_health_report()

    print(f"📈 Operations monitored: {op_report['total_operations']}")
    print(f"💚 System health - CPU: {health_report['cpu_usage']:.1f}%")

    # Export metrics
    monitor.export_metrics("metta_metrics_export.json")
    print("✅ Metrics exported to metta_metrics_export.json")

    print("\n🎉 MeTTa monitoring and logging demo complete!")

    # Cleanup
    monitor.shutdown()