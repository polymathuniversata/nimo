#!/usr/bin/env python3
"""
Cardano Integration Test Script

This script tests the Cardano service integration with the backend
to ensure everything is working properly after deployment.
"""

import os
import sys
import logging
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent / "backend"))

try:
    from services.cardano_service import cardano_service
    from services.metta_integration_enhanced import get_metta_service
    CARDSNO_AVAILABLE = True
except ImportError as e:
    print(f"❌ Import error: {e}")
    CARDSNO_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_cardano_service():
    """Test Cardano service functionality"""
    print("Testing Cardano Service...")
    print("-" * 30)

    if not cardano_service.available:
        print(f"❌ Cardano service not available: {cardano_service.error}")
        return False

    # Test network info
    try:
        network_info = cardano_service.get_network_info()
        print("✓ Network info retrieved"        print(f"  Network: {network_info.get('network')}")
        print(f"  Connected: {network_info.get('connected')}")
        if network_info.get('service_address'):
            print(f"  Service Address: {network_info['service_address']}")
    except Exception as e:
        print(f"❌ Network info test failed: {e}")
        return False

    # Test reward calculation
    try:
        reward_calc = cardano_service.get_reward_calculation(
            nimo_amount=100,
            confidence=0.85,
            contribution_type="coding"
        )
        print("✓ Reward calculation working"        print(f"  NIMO: {reward_calc['nimo_amount']}")
        print(f"  ADA: {reward_calc['final_ada_amount']}")
        print(f"  Pays ADA: {reward_calc['pays_ada']}")
    except Exception as e:
        print(f"❌ Reward calculation test failed: {e}")
        return False

    # Test transaction cost estimation
    try:
        cost_est = cardano_service.estimate_transaction_cost("send_ada")
        print("✓ Transaction cost estimation working"        print(f"  Fee: {cost_est.get('estimated_fee_ada', 'N/A')} ADA")
    except Exception as e:
        print(f"❌ Cost estimation test failed: {e}")
        return False

    return True

def test_metta_integration():
    """Test MeTTa integration"""
    print("\nTesting MeTTa Integration...")
    print("-" * 30)

    try:
        metta_service = get_metta_service()
        print("✓ MeTTa service initialized")

        # Test basic contribution validation
        test_contribution = {
            "category": "coding",
            "title": "Smart Contract Development",
            "evidence": ["github_link", "demo_video"],
            "description": "Developed a smart contract for decentralized identity"
        }

        result = metta_service.validate_contribution("test-contrib-123", test_contribution)

        if result:
            print("✓ MeTTa contribution validation working"            print(f"  Verified: {result.get('verified', False)}")
            print(f"  Confidence: {result.get('confidence', 0)}")
            print(f"  Token Award: {result.get('token_award', 0)}")
        else:
            print("⚠ MeTTa validation returned no result")

    except Exception as e:
        print(f"❌ MeTTa integration test failed: {e}")
        return False

    return True

def test_cardano_metta_integration():
    """Test Cardano + MeTTa integration"""
    print("\nTesting Cardano + MeTTa Integration...")
    print("-" * 40)

    try:
        metta_service = get_metta_service()

        # Create test contribution
        test_contribution = {
            "category": "coding",
            "title": "Blockchain Integration",
            "evidence": ["code_review", "unit_tests"],
            "description": "Integrated Cardano blockchain with MeTTa reasoning"
        }

        # Get MeTTa analysis
        metta_result = metta_service.validate_contribution("integration-test", test_contribution)

        if not metta_result or not metta_result.get('verified'):
            print("⚠ MeTTa validation failed or not verified")
            return False

        # Calculate Cardano reward
        reward_calc = cardano_service.get_reward_calculation(
            nimo_amount=metta_result.get('token_award', 50),
            confidence=metta_result.get('confidence', 0.8),
            contribution_type=test_contribution['category']
        )

        print("✓ Cardano + MeTTa integration working"        print(f"  MeTTa Confidence: {metta_result.get('confidence')}")
        print(f"  NIMO Tokens: {metta_result.get('token_award')}")
        print(f"  ADA Reward: {reward_calc.get('final_ada_amount')} ADA")
        print(f"  Total Value: {reward_calc.get('final_ada_amount', 0) + (metta_result.get('token_award', 0) / cardano_service.ada_to_nimo_rate)} ADA")

    except Exception as e:
        print(f"❌ Cardano + MeTTa integration test failed: {e}")
        return False

    return True

def main():
    """Main test function"""
    print("Cardano Integration Test Suite")
    print("=" * 40)
    print()

    if not CARDSNO_AVAILABLE:
        print("❌ Required modules not available")
        print("Make sure you're running from the project root")
        return 1

    test_results = []

    # Test Cardano service
    test_results.append(test_cardano_service())

    # Test MeTTa integration
    test_results.append(test_metta_integration())

    # Test combined integration
    test_results.append(test_cardano_metta_integration())

    # Summary
    print("\n" + "=" * 40)
    print("TEST SUMMARY")
    print("=" * 40)

    passed = sum(test_results)
    total = len(test_results)

    print(f"Tests Passed: {passed}/{total}")

    if passed == total:
        print("🎉 All tests passed! Cardano integration is ready.")
        print("\nYou can now:")
        print("- Start the backend server")
        print("- Use the Cardano API endpoints")
        print("- Process contributions with MeTTa + Cardano rewards")
    else:
        print("⚠️  Some tests failed. Check the output above.")

    return 0 if passed == total else 1

if __name__ == "__main__":
    exit(main())