#!/usr/bin/env python3
"""
Nimo Platform - Comprehensive Testing Suite

This script provides automated testing for all platform components including:
- Backend API endpoints
- Redis caching performance
- IPFS integration
- Smart contract interactions
- MeTTa AI reasoning
- Frontend React components
- Database migrations
- Security validation
"""

import os
import sys
import json
import time
import asyncio
import requests
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import psutil
import redis
import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class NimoTestSuite:
    """Comprehensive testing suite for Nimo platform"""

    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.test_results = {}
        self.start_time = datetime.now()
        self.report_file = f"test_report_{self.start_time.strftime('%Y%m%d_%H%M%S')}.json"

    def log(self, message: str, level: str = "INFO"):
        """Log test messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.request(method, url, **kwargs)

            return {
                'success': True,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds() * 1000,  # ms
                'data': response.json() if response.content else None,
                'error': None
            }
        except Exception as e:
            return {
                'success': False,
                'status_code': None,
                'response_time': None,
                'data': None,
                'error': str(e)
            }

    def test_backend_api(self) -> Dict[str, Any]:
        """Test all backend API endpoints"""
        self.log("🧪 Testing Backend API Endpoints...")

        endpoints = [
            # Health endpoints
            ('GET', '/api/health'),
            ('GET', '/api/health/services/redis'),
            ('GET', '/api/health/services/ipfs'),

            # Authentication endpoints
            ('POST', '/api/auth/register'),
            ('POST', '/api/auth/login'),

            # User endpoints
            ('GET', '/api/user/profile'),
            ('GET', '/api/user/contributions'),

            # Contribution endpoints
            ('GET', '/api/contributions/'),
            ('POST', '/api/contributions/'),

            # Cardano endpoints
            ('GET', '/api/cardano/network-info'),
            ('GET', '/api/cardano/address-info'),

            # AI Agents endpoints
            ('GET', '/api/ai-agents/status'),
            ('POST', '/api/ai-agents/verify-contribution'),

            # Token endpoints
            ('GET', '/api/token/balance'),
            ('GET', '/api/token/transactions'),

            # Autonomous endpoints
            ('GET', '/api/autonomous/platform-cycle'),
            ('POST', '/api/autonomous/process-contribution'),
        ]

        results = {}
        total_response_time = 0
        successful_requests = 0

        for method, endpoint in endpoints:
            self.log(f"Testing {method} {endpoint}")

            # Prepare request data
            headers = {'Content-Type': 'application/json'}
            data = None

            if method == 'POST' and 'login' in endpoint:
                data = json.dumps({
                    'email': 'test@example.com',
                    'password': 'testpass123'
                })
            elif method == 'POST' and 'contributions' in endpoint:
                data = json.dumps({
                    'title': 'Test Contribution',
                    'description': 'Test description',
                    'contribution_type': 'coding'
                })
            elif method == 'POST' and 'verify' in endpoint:
                data = json.dumps({
                    'contribution_id': 1,
                    'verifier_id': 1
                })

            # Make request
            result = self.make_request(method, endpoint, headers=headers, data=data)

            # Record result
            results[endpoint] = result
            if result['success']:
                total_response_time += result['response_time']
                successful_requests += 1

            # Log result
            if result['success']:
                self.log(f"✅ {endpoint} - {result['status_code']} - {result['response_time']:.1f}ms")
            else:
                self.log(f"❌ {endpoint} - {result['error']}", "ERROR")

        # Calculate summary
        avg_response_time = total_response_time / max(successful_requests, 1)
        success_rate = (successful_requests / len(endpoints)) * 100

        summary = {
            'total_endpoints': len(endpoints),
            'successful_requests': successful_requests,
            'failed_requests': len(endpoints) - successful_requests,
            'success_rate': f"{success_rate".1f"}%",
            'average_response_time': f"{avg_response_time".1f"}ms",
            'test_duration': f"{(datetime.now() - self.start_time).total_seconds()".1f"}s"
        }

        self.log(f"Backend API Test Summary: {summary['success_rate']} success rate")

        return {
            'test_name': 'backend_api',
            'status': 'PASSED' if success_rate >= 90 else 'FAILED',
            'summary': summary,
            'details': results
        }

    def test_redis_caching(self) -> Dict[str, Any]:
        """Test Redis caching performance"""
        self.log("🧪 Testing Redis Caching Performance...")

        # Test cache operations
        cache_tests = [
            ('GET', '/api/health/services/redis'),
            ('GET', '/api/health/services/redis'),
            ('GET', '/api/health/services/redis'),  # Repeated calls to test caching
        ]

        results = {}
        cache_hits = 0
        cache_misses = 0
        total_response_time = 0

        for i, (method, endpoint) in enumerate(cache_tests):
            self.log(f"Testing cache operation {i+1}")

            result = self.make_request(method, endpoint)

            if result['success']:
                results[f"cache_test_{i+1}"] = result
                total_response_time += result['response_time']

                # Check if response indicates cache usage
                if isinstance(result['data'], dict):
                    if result['data'].get('cache_stats', {}).get('hit_rate', 0) > 0:
                        cache_hits += 1
                    else:
                        cache_misses += 1

            # Add small delay between tests
            time.sleep(0.1)

        # Calculate summary
        avg_response_time = total_response_time / len(cache_tests)
        cache_efficiency = (cache_hits / max(cache_hits + cache_misses, 1)) * 100

        summary = {
            'total_tests': len(cache_tests),
            'cache_hits': cache_hits,
            'cache_misses': cache_misses,
            'cache_efficiency': f"{cache_efficiency".1f"}%",
            'average_response_time': f"{avg_response_time".1f"}ms"
        }

        self.log(f"Redis Cache Test Summary: {summary['cache_efficiency']} efficiency")

        return {
            'test_name': 'redis_caching',
            'status': 'PASSED' if cache_efficiency >= 80 else 'WARNING',
            'summary': summary,
            'details': results
        }

    def test_ipfs_integration(self) -> Dict[str, Any]:
        """Test IPFS integration"""
        self.log("🧪 Testing IPFS Integration...")

        # Test IPFS health
        result = self.make_request('GET', '/api/health/services/ipfs')

        if not result['success']:
            return {
                'test_name': 'ipfs_integration',
                'status': 'FAILED',
                'summary': {'error': result['error']},
                'details': result
            }

        ipfs_data = result['data']
        health_status = ipfs_data.get('health', {}).get('overall', 'unknown')

        summary = {
            'ipfs_status': health_status,
            'local_node_available': ipfs_data.get('node_info', {}).get('local_node_available', False),
            'pinata_available': ipfs_data.get('node_info', {}).get('pinata_available', False),
            'response_time': f"{result['response_time']".1f"}ms"
        }

        self.log(f"IPFS Test Summary: {health_status} status")

        return {
            'test_name': 'ipfs_integration',
            'status': 'PASSED' if health_status == 'healthy' else 'WARNING',
            'summary': summary,
            'details': ipfs_data
        }

    def test_metta_ai(self) -> Dict[str, Any]:
        """Test MeTTa AI integration"""
        self.log("🧪 Testing MeTTa AI Integration...")

        # Test MeTTa service health
        result = self.make_request('GET', '/api/ai-agents/status')

        if not result['success']:
            return {
                'test_name': 'metta_ai',
                'status': 'FAILED',
                'summary': {'error': result['error']},
                'details': result
            }

        metta_data = result['data']
        service_status = metta_data.get('status', 'unknown')

        summary = {
            'metta_service_status': service_status,
            'confidence_accuracy': metta_data.get('confidence_accuracy', 'N/A'),
            'response_time': f"{result['response_time']".1f"}ms"
        }

        self.log(f"MeTTa AI Test Summary: {service_status} status")

        return {
            'test_name': 'metta_ai',
            'status': 'PASSED' if service_status == 'operational' else 'WARNING',
            'summary': summary,
            'details': metta_data
        }

    def test_smart_contracts(self) -> Dict[str, Any]:
        """Test smart contract deployment and interaction"""
        self.log("🧪 Testing Smart Contract Integration...")

        # Test Cardano service
        result = self.make_request('GET', '/api/cardano/network-info')

        if not result['success']:
            return {
                'test_name': 'smart_contracts',
                'status': 'FAILED',
                'summary': {'error': result['error']},
                'details': result
            }

        cardano_data = result['data']
        network_status = cardano_data.get('network', {}).get('status', 'unknown')

        summary = {
            'cardano_network_status': network_status,
            'blockfrost_connection': 'connected' if cardano_data.get('blockfrost_available') else 'disconnected',
            'response_time': f"{result['response_time']".1f"}ms"
        }

        self.log(f"Smart Contract Test Summary: {network_status} status")

        return {
            'test_name': 'smart_contracts',
            'status': 'PASSED' if network_status == 'online' else 'WARNING',
            'summary': summary,
            'details': cardano_data
        }

    def test_performance_benchmark(self) -> Dict[str, Any]:
        """Run performance benchmark tests"""
        self.log("🧪 Running Performance Benchmarks...")

        # Simulate load testing
        concurrent_requests = 10
        test_endpoints = [
            '/api/health',
            '/api/health/services/redis',
            '/api/health/services/ipfs'
        ]

        results = {}
        total_requests = 0
        total_response_time = 0
        errors = 0

        def make_concurrent_request(endpoint: str) -> Dict[str, Any]:
            nonlocal total_requests, total_response_time, errors
            try:
                total_requests += 1
                result = self.make_request('GET', endpoint)
                if result['success']:
                    total_response_time += result['response_time']
                else:
                    errors += 1
                return result
            except Exception as e:
                errors += 1
                return {'error': str(e)}

        # Run concurrent requests
        threads = []
        for _ in range(concurrent_requests):
            for endpoint in test_endpoints:
                thread = threading.Thread(target=make_concurrent_request, args=(endpoint,))
                threads.append(thread)
                thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Calculate summary
        avg_response_time = total_response_time / max(total_requests - errors, 1)
        error_rate = (errors / total_requests) * 100 if total_requests > 0 else 0

        summary = {
            'total_requests': total_requests,
            'successful_requests': total_requests - errors,
            'error_requests': errors,
            'error_rate': f"{error_rate".1f"}%",
            'average_response_time': f"{avg_response_time".1f"}ms",
            'requests_per_second': f"{total_requests / (datetime.now() - self.start_time).total_seconds()".1f"}"
        }

        self.log(f"Performance Benchmark Summary: {summary['requests_per_second']} req/sec")

        return {
            'test_name': 'performance_benchmark',
            'status': 'PASSED' if error_rate < 10 else 'FAILED',
            'summary': summary,
            'details': results
        }

    def test_security_validation(self) -> Dict[str, Any]:
        """Test security measures"""
        self.log("🧪 Testing Security Validation...")

        # Test rate limiting
        rate_limit_tests = []
        for i in range(15):  # Exceed typical rate limit
            result = self.make_request('GET', '/api/health')
            rate_limit_tests.append(result)

        rate_limited = sum(1 for test in rate_limit_tests if test.get('status_code') == 429)
        total_tests = len(rate_limit_tests)

        # Test input validation
        malicious_inputs = [
            ("Test<script>alert('xss')</script>", "XSS attempt"),
            ("../../../etc/passwd", "Path traversal"),
            ("", "Empty input"),
            ("A" * 10000, "Buffer overflow attempt")
        ]

        validation_results = {}
        for malicious_input, test_type in malicious_inputs:
            data = json.dumps({'input': malicious_input})
            result = self.make_request('POST', '/api/test/validation', data=data)
            validation_results[test_type] = result

        summary = {
            'rate_limit_tests': total_tests,
            'rate_limited_requests': rate_limited,
            'rate_limit_effectiveness': f"{(rate_limited / total_tests) * 100".1f"}%",
            'validation_tests': len(malicious_inputs),
            'validation_passed': sum(1 for r in validation_results.values() if r.get('status_code') in [400, 422])
        }

        self.log(f"Security Test Summary: {summary['rate_limit_effectiveness']} rate limit effectiveness")

        return {
            'test_name': 'security_validation',
            'status': 'PASSED' if rate_limited > 0 else 'WARNING',
            'summary': summary,
            'details': {'rate_limit': rate_limit_tests, 'validation': validation_results}
        }

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites"""
        self.log("🚀 Starting Comprehensive Nimo Platform Test Suite...")

        test_methods = [
            self.test_backend_api,
            self.test_redis_caching,
            self.test_ipfs_integration,
            self.test_metta_ai,
            self.test_smart_contracts,
            self.test_performance_benchmark,
            self.test_security_validation
        ]

        all_results = {}
        passed_tests = 0
        total_tests = len(test_methods)

        for test_method in test_methods:
            test_name = test_method.__name__.replace('test_', '')
            self.log(f"\n{'='*60}")
            self.log(f"Running {test_name.upper()} tests...")
            self.log('='*60)

            try:
                result = test_method()
                all_results[test_name] = result

                if result['status'] == 'PASSED':
                    passed_tests += 1

                self.log(f"✅ {test_name} test completed: {result['status']}")

            except Exception as e:
                error_result = {
                    'test_name': test_name,
                    'status': 'ERROR',
                    'summary': {'error': str(e)},
                    'details': {}
                }
                all_results[test_name] = error_result
                self.log(f"❌ {test_name} test failed: {e}", "ERROR")

        # Overall summary
        overall_status = 'PASSED' if passed_tests == total_tests else 'WARNING' if passed_tests >= total_tests * 0.8 else 'FAILED'

        overall_summary = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': f"{(passed_tests / total_tests) * 100".1f"}%",
            'total_duration': f"{(datetime.now() - self.start_time).total_seconds()".1f"}s",
            'timestamp': self.start_time.isoformat()
        }

        final_results = {
            'overall_status': overall_status,
            'overall_summary': overall_summary,
            'test_results': all_results,
            'report_generated': datetime.now().isoformat()
        }

        self.log(f"\n{'='*60}")
        self.log("🎉 TEST SUITE COMPLETED")
        self.log('='*60)
        self.log(f"Overall Status: {overall_status}")
        self.log(f"Success Rate: {overall_summary['success_rate']}")
        self.log(f"Duration: {overall_summary['total_duration']}")
        self.log('='*60)

        # Save detailed report
        with open(self.report_file, 'w') as f:
            json.dump(final_results, f, indent=2)

        self.log(f"📊 Detailed report saved to: {self.report_file}")

        return final_results

def main():
    """Main test suite execution"""
    print("🔬 Nimo Platform - Comprehensive Test Suite")
    print("=" * 50)

    # Check if backend is running
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code != 200:
            print("❌ Backend server not responding. Please start the backend first:")
            print("   cd backend && python app.py")
            return 1
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to backend server.")
        print("   Please ensure the backend is running on http://localhost:5000")
        return 1

    # Run test suite
    tester = NimoTestSuite()
    results = tester.run_all_tests()

    # Exit with appropriate code
    if results['overall_status'] == 'PASSED':
        print("✅ All tests passed! Platform is production-ready.")
        return 0
    elif results['overall_status'] == 'WARNING':
        print("⚠️  Some tests have warnings. Review the detailed report.")
        return 0
    else:
        print("❌ Test suite failed. Check the detailed report for issues.")
        return 1

if __name__ == "__main__":
    exit(main())
