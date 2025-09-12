"""
Test Autonomous System Integration

This script tests the integration of the autonomous system with the Flask backend.
"""

import requests
import json
import time
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:5000"
TEST_USER_TOKEN = None  # Will be set after login

def test_health_check():
    """Test autonomous system health check"""
    print("Testing autonomous system health...")
    try:
        response = requests.get(f"{BASE_URL}/api/autonomous/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health check passed: {data['status']}")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False

def test_autonomous_status():
    """Test autonomous system status (requires auth)"""
    print("Testing autonomous system status...")
    if not TEST_USER_TOKEN:
        print("⚠ Skipping status test - no auth token")
        return False

    headers = {"Authorization": f"Bearer {TEST_USER_TOKEN}"}
    try:
        response = requests.get(f"{BASE_URL}/api/autonomous/status", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status check passed: {len(data['capabilities'])} capabilities available")
            return True
        else:
            print(f"✗ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Status check error: {e}")
        return False

def test_autonomous_cycle():
    """Test autonomous cycle execution"""
    print("Testing autonomous cycle execution...")
    if not TEST_USER_TOKEN:
        print("⚠ Skipping cycle test - no auth token")
        return False

    headers = {"Authorization": f"Bearer {TEST_USER_TOKEN}"}
    payload = {
        "platform_state": {
            "active_users": 1000,
            "total_contributions": 500,
            "platform_health": 0.85,
            "security_alerts": 2
        }
    }

    try:
        response = requests.post(f"{BASE_URL}/api/autonomous/cycle",
                               json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Autonomous cycle executed: {data['message']}")
            return True
        else:
            print(f"✗ Autonomous cycle failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Autonomous cycle error: {e}")
        return False

def test_contribution_processing():
    """Test autonomous contribution processing"""
    print("Testing autonomous contribution processing...")
    if not TEST_USER_TOKEN:
        print("⚠ Skipping contribution processing test - no auth token")
        return False

    headers = {"Authorization": f"Bearer {TEST_USER_TOKEN}"}
    contribution_id = "test-contrib-001"

    try:
        response = requests.post(f"{BASE_URL}/api/autonomous/contributions/{contribution_id}/process",
                               headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Contribution processed: {data['message']}")
            return True
        else:
            print(f"✗ Contribution processing failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Contribution processing error: {e}")
        return False

def test_predictive_optimization():
    """Test predictive platform optimization"""
    print("Testing predictive platform optimization...")
    if not TEST_USER_TOKEN:
        print("⚠ Skipping optimization test - no auth token")
        return False

    headers = {"Authorization": f"Bearer {TEST_USER_TOKEN}"}
    payload = {
        "platform_state": {
            "user_growth_rate": 0.15,
            "contribution_trends": [100, 120, 140, 160],
            "system_load": 0.7
        }
    }

    try:
        response = requests.post(f"{BASE_URL}/api/autonomous/platform/optimize",
                               json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Platform optimization completed: {data['message']}")
            return True
        else:
            print(f"✗ Platform optimization failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Platform optimization error: {e}")
        return False

def test_fraud_detection():
    """Test comprehensive fraud detection"""
    print("Testing comprehensive fraud detection...")
    if not TEST_USER_TOKEN:
        print("⚠ Skipping fraud detection test - no auth token")
        return False

    headers = {"Authorization": f"Bearer {TEST_USER_TOKEN}"}
    contribution_id = "test-contrib-fraud-001"

    try:
        response = requests.post(f"{BASE_URL}/api/autonomous/contributions/{contribution_id}/fraud-detect",
                               headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Fraud detection completed: {data['message']}")
            return True
        else:
            print(f"✗ Fraud detection failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Fraud detection error: {e}")
        return False

def test_predictive_insights():
    """Test predictive insights analysis"""
    print("Testing predictive insights analysis...")
    if not TEST_USER_TOKEN:
        print("⚠ Skipping predictive insights test - no auth token")
        return False

    headers = {"Authorization": f"Bearer {TEST_USER_TOKEN}"}
    payload = {
        "entity_id": "test-entity-001",
        "prediction_type": "user-engagement"
    }

    try:
        response = requests.post(f"{BASE_URL}/api/autonomous/analytics/predict",
                               json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Predictive analysis completed: {data['message']}")
            return True
        else:
            print(f"✗ Predictive analysis failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Predictive analysis error: {e}")
        return False

def run_integration_tests():
    """Run all integration tests"""
    print("=" * 60)
    print("AUTONOMOUS SYSTEM INTEGRATION TESTS")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # Test results
    results = []

    # Test 1: Health check (no auth required)
    results.append(("Health Check", test_health_check()))

    # Test 2: Autonomous status (requires auth)
    results.append(("Autonomous Status", test_autonomous_status()))

    # Test 3: Autonomous cycle
    results.append(("Autonomous Cycle", test_autonomous_cycle()))

    # Test 4: Contribution processing
    results.append(("Contribution Processing", test_contribution_processing()))

    # Test 5: Predictive optimization
    results.append(("Predictive Optimization", test_predictive_optimization()))

    # Test 6: Fraud detection
    results.append(("Fraud Detection", test_fraud_detection()))

    # Test 7: Predictive insights
    results.append(("Predictive Insights", test_predictive_insights()))

    # Summary
    print()
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} {test_name}")

    print()
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("🎉 All autonomous system integration tests passed!")
        return True
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = run_integration_tests()
    exit(0 if success else 1)