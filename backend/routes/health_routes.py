"""
Health Check and Monitoring Endpoints for Nimo Backend

This module provides comprehensive health check endpoints for monitoring
system status, performance metrics, and autonomous operations.
"""

import time
import psutil
import json
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from typing import Dict, Any

# Import services
from services.metta_integration_enhanced import get_metta_service
from services.metta_performance_monitor import get_monitor
from services.metta_query_optimizer import get_optimized_query_service

# Create blueprint
health_bp = Blueprint('health', __name__, url_prefix='/api/health')

def get_system_metrics() -> Dict[str, Any]:
    """Get comprehensive system metrics"""
    try:
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent,
                'used': psutil.virtual_memory().used
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'free': psutil.disk_usage('/').free,
                'used': psutil.disk_usage('/').used,
                'percent': psutil.disk_usage('/').percent
            },
            'network': {
                'bytes_sent': psutil.net_io_counters().bytes_sent,
                'bytes_recv': psutil.net_io_counters().bytes_recv,
                'packets_sent': psutil.net_io_counters().packets_sent,
                'packets_recv': psutil.net_io_counters().packets_recv
            },
            'uptime_seconds': time.time() - psutil.boot_time(),
            'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        }
    except Exception as e:
        return {
            'error': f'Failed to get system metrics: {str(e)}',
            'cpu_percent': 0,
            'memory': {'percent': 0},
            'disk': {'percent': 0}
        }

def get_service_health() -> Dict[str, Any]:
    """Get comprehensive service health information"""
    health_info = {
        'timestamp': datetime.now().isoformat(),
        'services': {},
        'overall_status': 'healthy',
        'issues': []
    }

    # Check MeTTa service
    try:
        metta_service = get_metta_service()
        service_health = metta_service.get_service_health()

        health_info['services']['metta_integration'] = {
            'status': 'healthy' if service_health.get('overall_healthy', False) else 'unhealthy',
            'mode': service_health.get('components', {}).get('base_service', {}).get('mode', 'unknown'),
            'connected': service_health.get('components', {}).get('base_service', {}).get('connected', False),
            'components': service_health.get('components', {})
        }

        if not service_health.get('overall_healthy', False):
            health_info['issues'].append('MeTTa integration service has issues')
            health_info['overall_status'] = 'degraded'

    except Exception as e:
        health_info['services']['metta_integration'] = {
            'status': 'error',
            'error': str(e)
        }
        health_info['issues'].append(f'MeTTa service error: {str(e)}')
        health_info['overall_status'] = 'unhealthy'

    # Check performance monitor
    try:
        monitor = get_monitor()
        if monitor:
            health_info['services']['performance_monitor'] = {
                'status': 'healthy',
                'active_operations': len(monitor.active_operations),
                'total_operations': sum(monitor.operation_counts.values())
            }
        else:
            health_info['services']['performance_monitor'] = {
                'status': 'unavailable'
            }
    except Exception as e:
        health_info['services']['performance_monitor'] = {
            'status': 'error',
            'error': str(e)
        }

    # Check query optimizer
    try:
        optimizer = get_optimized_query_service()
        if optimizer:
            optimizer_health = optimizer.health_check()
            health_info['services']['query_optimizer'] = optimizer_health

            if optimizer_health.get('status') != 'healthy':
                health_info['issues'].append('Query optimizer has issues')
                if health_info['overall_status'] == 'healthy':
                    health_info['overall_status'] = 'degraded'
        else:
            health_info['services']['query_optimizer'] = {
                'status': 'unavailable'
            }
    except Exception as e:
        health_info['services']['query_optimizer'] = {
            'status': 'error',
            'error': str(e)
        }

    return health_info

@health_bp.route('/', methods=['GET'])
def health_check():
    """
    Basic health check endpoint

    Returns:
        JSON response with basic health status
    """
    try:
        service_health = get_service_health()
        system_metrics = get_system_metrics()

        response = {
            'status': service_health['overall_status'],
            'timestamp': service_health['timestamp'],
            'version': '1.0.0',
            'services': {
                name: {'status': info['status']}
                for name, info in service_health['services'].items()
            },
            'system': {
                'cpu_percent': system_metrics['cpu_percent'],
                'memory_percent': system_metrics['memory']['percent'],
                'disk_percent': system_metrics['disk']['percent']
            }
        }

        # Set HTTP status code based on health
        status_code = 200
        if service_health['overall_status'] == 'unhealthy':
            status_code = 503  # Service Unavailable
        elif service_health['overall_status'] == 'degraded':
            status_code = 200  # Still OK but with warnings

        return jsonify(response), status_code

    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@health_bp.route('/detailed', methods=['GET'])
def detailed_health_check():
    """
    Detailed health check with comprehensive information

    Query parameters:
        include_metrics: Include detailed system metrics (default: true)
        include_performance: Include performance statistics (default: true)
        time_window: Time window for performance stats in seconds (default: 3600)

    Returns:
        JSON response with detailed health information
    """
    try:
        include_metrics = request.args.get('include_metrics', 'true').lower() == 'true'
        include_performance = request.args.get('include_performance', 'true').lower() == 'true'
        time_window = int(request.args.get('time_window', 3600))

        # Get basic health info
        service_health = get_service_health()

        response = {
            'status': service_health['overall_status'],
            'timestamp': service_health['timestamp'],
            'version': '1.0.0',
            'services': service_health['services'],
            'issues': service_health['issues']
        }

        # Add system metrics if requested
        if include_metrics:
            response['system_metrics'] = get_system_metrics()

        # Add performance statistics if requested
        if include_performance:
            try:
                monitor = get_monitor()
                if monitor:
                    response['performance'] = monitor.get_performance_report(time_window)

                optimizer = get_optimized_query_service()
                if optimizer:
                    response['query_performance'] = optimizer.get_performance_stats()

            except Exception as e:
                response['performance_error'] = str(e)

        # Set HTTP status code
        status_code = 200
        if service_health['overall_status'] == 'unhealthy':
            status_code = 503
        elif service_health['overall_status'] == 'degraded':
            status_code = 200

        return jsonify(response), status_code

    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@health_bp.route('/services/<service_name>', methods=['GET'])
def service_health_check(service_name: str):
    """
    Health check for a specific service

    Args:
        service_name: Name of the service to check

    Returns:
        JSON response with service-specific health information
    """
    try:
        service_health = get_service_health()

        if service_name not in service_health['services']:
            return jsonify({
                'error': f'Service {service_name} not found',
                'available_services': list(service_health['services'].keys())
            }), 404

        service_info = service_health['services'][service_name]

        # Add additional service-specific information
        if service_name == 'metta_integration':
            try:
                metta_service = get_metta_service()
                service_info['connection_status'] = metta_service.is_connected()
                service_info['service_info'] = metta_service.get_service_info()
            except Exception as e:
                service_info['connection_error'] = str(e)

        elif service_name == 'performance_monitor':
            try:
                monitor = get_monitor()
                if monitor:
                    service_info['active_operations'] = len(monitor.active_operations)
                    service_info['operation_counts'] = dict(monitor.operation_counts)
                    service_info['error_counts'] = dict(monitor.error_counts)
            except Exception as e:
                service_info['monitor_error'] = str(e)

        elif service_name == 'query_optimizer':
            try:
                optimizer = get_optimized_query_service()
                if optimizer:
                    service_info['connection_pool'] = optimizer.connection_pool.get_pool_stats()
                    service_info['performance_stats'] = optimizer.get_performance_stats()
            except Exception as e:
                service_info['optimizer_error'] = str(e)

        response = {
            'service': service_name,
            'status': service_info['status'],
            'timestamp': service_health['timestamp'],
            'details': service_info
        }

        status_code = 200 if service_info['status'] in ['healthy', 'available'] else 503

        return jsonify(response), status_code

    except Exception as e:
        return jsonify({
            'service': service_name,
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@health_bp.route('/metrics', methods=['GET'])
def system_metrics():
    """
    System metrics endpoint

    Returns:
        JSON response with detailed system metrics
    """
    try:
        metrics = get_system_metrics()
        metrics['timestamp'] = datetime.now().isoformat()

        return jsonify(metrics), 200

    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@health_bp.route('/performance', methods=['GET'])
def performance_metrics():
    """
    Performance metrics endpoint

    Query parameters:
        time_window: Time window in seconds (default: 3600)
        format: Response format - 'summary' or 'detailed' (default: 'summary')

    Returns:
        JSON response with performance metrics
    """
    try:
        time_window = int(request.args.get('time_window', 3600))
        format_type = request.args.get('format', 'summary')

        monitor = get_monitor()
        if not monitor:
            return jsonify({
                'error': 'Performance monitor not available',
                'timestamp': datetime.now().isoformat()
            }), 503

        if format_type == 'detailed':
            report = monitor.get_performance_report(time_window)
        else:
            # Summary format
            report = monitor.get_performance_report(time_window)
            # Extract key summary information
            report = {
                'summary': {
                    'total_operations': sum(
                        stats.get('total_operations', 0)
                        for stats in report.get('operation_stats', {}).get('operations', {}).values()
                    ),
                    'success_rate': sum(
                        stats.get('success_rate', 0)
                        for stats in report.get('operation_stats', {}).get('operations', {}).values()
                    ) / max(1, len(report.get('operation_stats', {}).get('operations', {}))),
                    'active_operations': report.get('operation_stats', {}).get('summary', {}).get('active_operations', 0),
                    'bottlenecks': len(report.get('bottlenecks', []))
                },
                'timestamp': report.get('generated_at'),
                'time_window_seconds': time_window
            }

        return jsonify(report), 200

    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@health_bp.route('/autonomous', methods=['GET'])
def autonomous_operations_health():
    """
    Health check for autonomous operations

    Returns:
        JSON response with autonomous operations status
    """
    try:
        metta_service = get_metta_service()

        # Test autonomous operations
        test_results = {
            'timestamp': datetime.now().isoformat(),
            'autonomous_operations': {}
        }

        # Test platform cycle
        try:
            platform_state = {'test': True, 'active_users': 1}
            result = metta_service.execute_autonomous_cycle(platform_state)
            test_results['autonomous_operations']['platform_cycle'] = {
                'status': 'operational' if result else 'failed',
                'response_time': 0  # Would need timing decorator
            }
        except Exception as e:
            test_results['autonomous_operations']['platform_cycle'] = {
                'status': 'error',
                'error': str(e)
            }

        # Test contribution processing
        try:
            result = metta_service.process_contribution_autonomously('test_123')
            test_results['autonomous_operations']['contribution_processing'] = {
                'status': 'operational' if result else 'failed'
            }
        except Exception as e:
            test_results['autonomous_operations']['contribution_processing'] = {
                'status': 'error',
                'error': str(e)
            }

        # Test reward calculation
        try:
            result = metta_service.calculate_autonomous_reward('test_123', 0.8, 0.7)
            test_results['autonomous_operations']['reward_calculation'] = {
                'status': 'operational' if result else 'failed'
            }
        except Exception as e:
            test_results['autonomous_operations']['reward_calculation'] = {
                'status': 'error',
                'error': str(e)
            }

        # Determine overall status
        operations_status = test_results['autonomous_operations']
        operational_count = sum(1 for op in operations_status.values() if op['status'] == 'operational')
        total_count = len(operations_status)

        test_results['overall_status'] = 'healthy' if operational_count == total_count else 'degraded'
        test_results['operational_count'] = operational_count
        test_results['total_operations'] = total_count

        status_code = 200 if test_results['overall_status'] == 'healthy' else 503

        return jsonify(test_results), status_code

    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@health_bp.route('/ready', methods=['GET'])
def readiness_check():
    """
    Kubernetes-style readiness check

    Returns:
        200 if service is ready to serve requests
        503 if service is not ready
    """
    try:
        service_health = get_service_health()

        if service_health['overall_status'] in ['healthy', 'degraded']:
            return jsonify({
                'status': 'ready',
                'timestamp': service_health['timestamp']
            }), 200
        else:
            return jsonify({
                'status': 'not ready',
                'issues': service_health['issues'],
                'timestamp': service_health['timestamp']
            }), 503

    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503

@health_bp.route('/live', methods=['GET'])
def liveness_check():
    """
    Kubernetes-style liveness check

    Returns:
        200 if service is alive and responding
        503 if service is dead or unresponsive
    """
    # Simple liveness check - if we can respond, we're alive
    return jsonify({
        'status': 'alive',
        'timestamp': datetime.now().isoformat()
    }), 200

# Export the blueprint
__all__ = ['health_bp']