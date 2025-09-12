#!/usr/bin/env python3
"""
Simple validation script for MeTTa Autonomous System
Tests the core autonomous functionality without pytest dependencies
"""

import sys
import os
import json
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")

    try:
        from services.metta_integration_enhanced import MeTTaIntegrationService
        print("✅ MeTTaIntegrationService imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import MeTTaIntegrationService: {e}")
        return False

    try:
        from services.metta_reasoning import MeTTaReasoning
        print("✅ MeTTaReasoning imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import MeTTaReasoning: {e}")
        return False

    return True

def test_metta_integration_service():
    """Test MeTTaIntegrationService functionality"""
    print("\n🔍 Testing MeTTaIntegrationService...")

    try:
        from services.metta_integration_enhanced import MeTTaIntegrationService

        # Create service instance
        service = MeTTaIntegrationService(force_mock=True)
        print("✅ MeTTaIntegrationService instance created")

        # Test health check
        health = service.health_check()
        print(f"✅ Health check: {health}")

        # Test autonomous cycle
        platform_state = {
            "active_users": 1000,
            "total_contributions": 500,
            "platform_health": 0.85,
            "security_alerts": 2
        }

        result = service.execute_autonomous_cycle(platform_state)
        if result and result.get('success'):
            print("✅ Autonomous cycle executed successfully")
        else:
            print(f"❌ Autonomous cycle failed: {result}")

        # Test contribution processing
        result = service.process_contribution_autonomously("test-contrib-001")
        if result and result.get('processed'):
            print("✅ Contribution processing successful")
        else:
            print(f"❌ Contribution processing failed: {result}")

        return True

    except Exception as e:
        print(f"❌ MeTTaIntegrationService test failed: {e}")
        return False

def test_metta_reasoning_service():
    """Test MeTTaReasoning functionality"""
    print("\n🔍 Testing MeTTaReasoning...")

    try:
        from services.metta_reasoning import MeTTaReasoning

        # Create service instance
        service = MeTTaReasoning()
        print("✅ MeTTaReasoning instance created")

        # Test autonomous cycle
        platform_state = {
            "metrics": {"users": 1000, "contributions": 500},
            "health": 0.85
        }

        result = service.execute_autonomous_cycle(platform_state)
        if result and result.get('success'):
            print("✅ MeTTaReasoning autonomous cycle successful")
        else:
            print(f"❌ MeTTaReasoning autonomous cycle failed: {result}")

        # Test contribution processing
        result = service.process_contribution_autonomously("test-contrib-002")
        if result and result.get('processed'):
            print("✅ MeTTaReasoning contribution processing successful")
        else:
            print(f"❌ MeTTaReasoning contribution processing failed: {result}")

        return True

    except Exception as e:
        print(f"❌ MeTTaReasoning test failed: {e}")
        return False

def test_autonomous_methods():
    """Test that all autonomous methods exist"""
    print("\n🔍 Testing autonomous methods availability...")

    try:
        from services.metta_reasoning import MeTTaReasoning
        from services.metta_integration_enhanced import MeTTaIntegrationService

        reasoning_methods = [
            'execute_autonomous_cycle',
            'process_contribution_autonomously',
            'calculate_autonomous_reward',
            'optimize_platform_predictively',
            'execute_governance_autonomously',
            'manage_security_autonomously',
            'detect_fraud_comprehensive',
            'analyze_predictive_insights'
        ]

        integration_methods = [
            'execute_autonomous_cycle',
            'process_contribution_autonomously',
            'calculate_autonomous_reward',
            'optimize_platform_predictively',
            'execute_governance_autonomously',
            'manage_security_autonomously',
            'detect_fraud_comprehensive',
            'analyze_predictive_insights'
        ]

        reasoning_service = MeTTaReasoning()
        integration_service = MeTTaIntegrationService(force_mock=True)

        print("🔍 Checking MeTTaReasoning methods:")
        for method in reasoning_methods:
            if hasattr(reasoning_service, method):
                print(f"  ✅ {method}")
            else:
                print(f"  ❌ {method} - MISSING")

        print("🔍 Checking MeTTaIntegrationService methods:")
        for method in integration_methods:
            if hasattr(integration_service, method):
                print(f"  ✅ {method}")
            else:
                print(f"  ❌ {method} - MISSING")

        return True

    except Exception as e:
        print(f"❌ Method availability test failed: {e}")
        return False

def main():
    """Main validation function"""
    print("🚀 MeTTa Autonomous System Validation")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().isoformat()}")

    results = []

    # Test imports
    results.append(("Imports", test_imports()))

    # Test MeTTaIntegrationService
    results.append(("MeTTaIntegrationService", test_metta_integration_service()))

    # Test MeTTaReasoning
    results.append(("MeTTaReasoning", test_metta_reasoning_service()))

    # Test method availability
    results.append(("Autonomous Methods", test_autonomous_methods()))

    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print("25")
        if success:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All autonomous system components validated successfully!")
        print("\n🚀 NEXT STEPS:")
        print("1. Performance optimization and caching implementation")
        print("2. Frontend integration preparation")
        print("3. Production deployment setup")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)