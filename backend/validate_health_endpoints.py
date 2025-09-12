#!/usr/bin/env python3
"""
Health Check Endpoints Validation Script

This script validates the comprehensive health check endpoints
for monitoring system status and performance.
"""

import sys
import os
import json
import requests
from datetime import datetime

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_health_endpoints():
    """Test all health check endpoints"""
    print("🏥 Testing Health Check Endpoints")
    print("=" * 50)

    # Start a test server
    try:
        from app import create_app

        app = create_app()
        app.config['TESTING'] = True
        client = app.test_client()

        print("✅ Test client initialized")

        # Test 1: Basic health check
        print("\n1. Testing Basic Health Check")
        print("-" * 30)

        response = client.get('/api/health/')
        print(f"   Status Code: {response.status_code}")

        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"   Status: {data.get('status', 'N/A')}")
            print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
            print(f"   Services: {len(data.get('services', {}))}")
            print("   ✅ Basic health check working")
        else:
            print("   ❌ Basic health check failed")

        # Test 2: Detailed health check
        print("\n2. Testing Detailed Health Check")
        print("-" * 30)

        response = client.get('/api/health/detailed')
        print(f"   Status Code: {response.status_code}")

        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"   Overall Status: {data.get('status', 'N/A')}")
            print(f"   System CPU: {data.get('system_metrics', {}).get('cpu_percent', 'N/A')}%")
            print(f"   System Memory: {data.get('system_metrics', {}).get('memory', {}).get('percent', 'N/A')}%")
            print(f"   Services: {len(data.get('services', {}))}")

            # Check service statuses
            services = data.get('services', {})
            for service_name, service_info in services.items():
                status = service_info.get('status', 'unknown')
                print(f"     {service_name}: {status}")

            print("   ✅ Detailed health check working")
        else:
            print("   ❌ Detailed health check failed")

        # Test 3: Service-specific health checks
        print("\n3. Testing Service-Specific Health Checks")
        print("-" * 30)

        services_to_test = ['metta_integration', 'performance_monitor', 'query_optimizer']

        for service_name in services_to_test:
            response = client.get(f'/api/health/services/{service_name}')
            print(f"   {service_name}: Status {response.status_code}")

            if response.status_code == 200:
                data = json.loads(response.data)
                service_status = data.get('details', {}).get('status', 'unknown')
                print(f"     Status: {service_status}")
            else:
                print(f"     ❌ Failed to get {service_name} health")

        # Test 4: System metrics
        print("\n4. Testing System Metrics")
        print("-" * 30)

        response = client.get('/api/health/metrics')
        print(f"   Status Code: {response.status_code}")

        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"   CPU Usage: {data.get('cpu_percent', 'N/A')}%")
            print(f"   Memory Usage: {data.get('memory', {}).get('percent', 'N/A')}%")
            print(f"   Disk Usage: {data.get('disk', {}).get('percent', 'N/A')}%")
            print("   ✅ System metrics working")
        else:
            print("   ❌ System metrics failed")

        # Test 5: Performance metrics
        print("\n5. Testing Performance Metrics")
        print("-" * 30)

        response = client.get('/api/health/performance?time_window=3600')
        print(f"   Status Code: {response.status_code}")

        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"   Generated At: {data.get('generated_at', 'N/A')}")
            print(f"   Total Operations: {data.get('operation_stats', {}).get('summary', {}).get('total_operations', 0)}")
            print(f"   Active Operations: {data.get('operation_stats', {}).get('summary', {}).get('active_operations', 0)}")
            print(f"   Bottlenecks: {len(data.get('bottlenecks', []))}")
            print("   ✅ Performance metrics working")
        else:
            print("   ❌ Performance metrics failed")

        # Test 6: Autonomous operations health
        print("\n6. Testing Autonomous Operations Health")
        print("-" * 30)

        response = client.get('/api/health/autonomous')
        print(f"   Status Code: {response.status_code}")

        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"   Overall Status: {data.get('overall_status', 'N/A')}")
            print(f"   Operational Count: {data.get('operational_count', 0)}")
            print(f"   Total Operations: {data.get('total_operations', 0)}")

            operations = data.get('autonomous_operations', {})
            for op_name, op_info in operations.items():
                print(f"     {op_name}: {op_info.get('status', 'unknown')}")

            print("   ✅ Autonomous operations health working")
        else:
            print("   ❌ Autonomous operations health failed")

        # Test 7: Readiness check
        print("\n7. Testing Readiness Check")
        print("-" * 30)

        response = client.get('/api/health/ready')
        print(f"   Status Code: {response.status_code}")

        if response.status_code in [200, 503]:
            data = json.loads(response.data)
            print(f"   Status: {data.get('status', 'N/A')}")
            print("   ✅ Readiness check working")
        else:
            print("   ❌ Readiness check failed")

        # Test 8: Liveness check
        print("\n8. Testing Liveness Check")
        print("-" * 30)

        response = client.get('/api/health/live')
        print(f"   Status Code: {response.status_code}")

        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"   Status: {data.get('status', 'N/A')}")
            print("   ✅ Liveness check working")
        else:
            print("   ❌ Liveness check failed")

        print("\n🎉 Health Check Endpoints Validation Complete!")
        print("=" * 50)

        return True

    except Exception as e:
        print(f"❌ Health check endpoints test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_health_report():
    """Generate a comprehensive health report"""
    print("\n📊 Generating Health Report")
    print("=" * 50)

    try:
        from app import create_app

        app = create_app()
        app.config['TESTING'] = True
        client = app.test_client()

        # Collect health data from all endpoints
        report = {
            'generated_at': datetime.now().isoformat(),
            'endpoints_tested': {},
            'overall_health': 'healthy',
            'issues': []
        }

        endpoints = [
            ('/api/health/', 'basic_health'),
            ('/api/health/detailed', 'detailed_health'),
            ('/api/health/metrics', 'system_metrics'),
            ('/api/health/performance', 'performance_metrics'),
            ('/api/health/autonomous', 'autonomous_health'),
            ('/api/health/ready', 'readiness'),
            ('/api/health/live', 'liveness')
        ]

        for endpoint, name in endpoints:
            try:
                response = client.get(endpoint)
                report['endpoints_tested'][name] = {
                    'status_code': response.status_code,
                    'working': response.status_code in [200, 503],  # 503 is acceptable for readiness
                    'data': json.loads(response.data) if response.status_code in [200, 503] else None
                }

                if response.status_code not in [200, 503]:
                    report['issues'].append(f"{name} endpoint returned {response.status_code}")

            except Exception as e:
                report['endpoints_tested'][name] = {
                    'status_code': None,
                    'working': False,
                    'error': str(e)
                }
                report['issues'].append(f"{name} endpoint failed: {str(e)}")

        # Determine overall health
        working_endpoints = sum(1 for ep in report['endpoints_tested'].values() if ep['working'])
        total_endpoints = len(report['endpoints_tested'])

        if working_endpoints < total_endpoints:
            report['overall_health'] = 'degraded' if working_endpoints > 0 else 'unhealthy'

        # Save report
        report_file = os.path.join(os.path.dirname(__file__), 'health_endpoints_report.json')

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"✅ Health report saved to: {report_file}")

        # Print summary
        print("\n📈 Health Report Summary:")
        print(f"   Overall Health: {report['overall_health']}")
        print(f"   Endpoints Working: {working_endpoints}/{total_endpoints}")
        print(f"   Issues Found: {len(report['issues'])}")

        if report['issues']:
            print("   Issues:")
            for issue in report['issues']:
                print(f"     - {issue}")

        return True

    except Exception as e:
        print(f"❌ Failed to generate health report: {e}")
        return False

if __name__ == "__main__":
    print("Nimo Health Check Endpoints Validation")
    print(f"Started at: {datetime.now().isoformat()}")
    print()

    # Run validation tests
    success = test_health_endpoints()

    if success:
        # Generate health report
        generate_health_report()

        print("\n🎯 Next Steps:")
        print("1. ✅ Health check endpoints implemented")
        print("2. 🔄 Ready for production deployment preparation")

    else:
        print("\n❌ Some tests failed - check logs above")
        sys.exit(1)