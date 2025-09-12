from flask import Blueprint, jsonify, current_app
from datetime import datetime, timedelta
import psutil
import os
import requests
from sqlalchemy import text
from ..models import db
from ..services.blockchain_service import BlockchainService
from ..services.metta_service import MettaService
from ..services.wallet_service import WalletService

health_bp = Blueprint('health', __name__)

class HealthChecker:
    """Comprehensive health checking for Nimo services"""

    def __init__(self):
        self.last_checks = {}
        self.check_interval = timedelta(minutes=5)

    def check_database(self):
        """Check database connectivity and performance"""
        try:
            start_time = datetime.utcnow()
            # Simple query to test connection
            db.session.execute(text('SELECT 1'))
            response_time = (datetime.utcnow() - start_time).total_seconds()

            return {
                'status': 'healthy',
                'response_time': response_time,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def check_blockchain(self):
        """Check blockchain connectivity"""
        try:
            blockchain_service = BlockchainService()
            # Test basic blockchain connectivity
            is_connected = blockchain_service.test_connection()

            return {
                'status': 'healthy' if is_connected else 'unhealthy',
                'network': os.getenv('CARDANO_NETWORK', 'testnet'),
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def check_metta_engine(self):
        """Check MeTTa engine status"""
        try:
            metta_service = MettaService()
            # Test MeTTa engine connectivity
            is_active = metta_service.test_connection()

            return {
                'status': 'healthy' if is_active else 'unhealthy',
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def check_wallet_service(self):
        """Check wallet service status"""
        try:
            wallet_service = WalletService()
            # Test wallet service availability
            is_available = wallet_service.test_service()

            return {
                'status': 'healthy' if is_available else 'unhealthy',
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def check_system_resources(self):
        """Check system resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            return {
                'status': 'healthy',
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'disk_usage': disk.percent,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def get_overall_health(self):
        """Get overall system health status"""
        checks = {
            'database': self.check_database(),
            'blockchain': self.check_blockchain(),
            'metta_engine': self.check_metta_engine(),
            'wallet_service': self.check_wallet_service(),
            'system_resources': self.check_system_resources()
        }

        # Determine overall status
        unhealthy_services = [service for service, result in checks.items()
                            if result.get('status') == 'unhealthy']

        overall_status = 'unhealthy' if unhealthy_services else 'healthy'

        return {
            'status': overall_status,
            'timestamp': datetime.utcnow().isoformat(),
            'services': checks,
            'unhealthy_services': unhealthy_services if unhealthy_services else None
        }

# Global health checker instance
health_checker = HealthChecker()

@health_bp.route('/health')
def overall_health():
    """Overall system health check"""
    health_data = health_checker.get_overall_health()

    status_code = 200 if health_data['status'] == 'healthy' else 503

    # Log health check results
    if hasattr(current_app, 'app_logger'):
        current_app.app_logger.info('Health check performed', extra=health_data)

    return jsonify(health_data), status_code

@health_bp.route('/health/database')
def database_health():
    """Database health check"""
    result = health_checker.check_database()
    status_code = 200 if result['status'] == 'healthy' else 503
    return jsonify(result), status_code

@health_bp.route('/health/blockchain')
def blockchain_health():
    """Blockchain health check"""
    result = health_checker.check_blockchain()
    status_code = 200 if result['status'] == 'healthy' else 503
    return jsonify(result), status_code

@health_bp.route('/health/metta')
def metta_health():
    """MeTTa engine health check"""
    result = health_checker.check_metta_engine()
    status_code = 200 if result['status'] == 'healthy' else 503
    return jsonify(result), status_code

@health_bp.route('/health/wallet')
def wallet_health():
    """Wallet service health check"""
    result = health_checker.check_wallet_service()
    status_code = 200 if result['status'] == 'healthy' else 503
    return jsonify(result), status_code

@health_bp.route('/health/system')
def system_health():
    """System resources health check"""
    result = health_checker.check_system_resources()
    status_code = 200 if result['status'] == 'healthy' else 503
    return jsonify(result), status_code

@health_bp.route('/metrics')
def metrics():
    """Prometheus-style metrics endpoint"""
    health_data = health_checker.get_overall_health()

    metrics_output = []

    # Overall health metric
    status_value = 1 if health_data['status'] == 'healthy' else 0
    metrics_output.append(f'# HELP nimo_health_status Overall system health status')
    metrics_output.append(f'# TYPE nimo_health_status gauge')
    metrics_output.append(f'nimo_health_status {status_value}')

    # Individual service metrics
    for service_name, service_data in health_data['services'].items():
        status_value = 1 if service_data.get('status') == 'healthy' else 0
        metrics_output.append(f'# HELP nimo_{service_name}_health {service_name} service health status')
        metrics_output.append(f'# TYPE nimo_{service_name}_health gauge')
        metrics_output.append(f'nimo_{service_name}_health {status_value}')

        # Response time metrics where available
        if 'response_time' in service_data:
            metrics_output.append(f'# HELP nimo_{service_name}_response_time {service_name} response time in seconds')
            metrics_output.append(f'# TYPE nimo_{service_name}_response_time gauge')
            metrics_output.append(f'nimo_{service_name}_response_time {service_data["response_time"]}')

    return '\n'.join(metrics_output), 200, {'Content-Type': 'text/plain; charset=utf-8'}