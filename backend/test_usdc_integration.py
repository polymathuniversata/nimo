#!/usr/bin/env python3
"""
Test Cardano Token Integration with MeTTa Rewards System

This script tests the complete flow of MeTTa reasoning → NIMO tokens → Cardano ADA rewards
MIGRATED FROM: USDC Integration Tests
"""

import sys
import os
import json
import logging
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

# Import Cardano services (replacing USDC imports)
from services.cardano_service import CardanoService
from services.blockchain_token_service import BlockchainTokenService
from services.token_service import TokenService
from services.metta_integration_enhanced import get_metta_service
from services.metta_blockchain_bridge import MeTTaBlockchainBridge

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CardanoIntegrationTester:
    def __init__(self):
        """Initialize test environment with Cardano services"""
        self.cardano_service = CardanoService()
        self.token_service = BlockchainTokenService()
        self.unified_token_service = TokenService()
        self.metta_integration = get_metta_service()

        # Try to initialize blockchain bridge
        try:
            self.bridge = MeTTaBlockchainBridge(self.cardano_service, self.metta_integration)
        except Exception as e:
            logger.warning(f"Blockchain bridge not available: {e}")
            self.bridge = None
    
    def test_network_connection(self):
        """Test 1: Network connection and status"""
        logger.info("🌐 Test 1: Cardano Network Connection")

        try:
            network_status = self.cardano_service.get_network_status()
            logger.info(f"   Network: {network_status.get('network', 'cardano')}")
            logger.info(f"   Connected: {network_status.get('connected', False)}")
            logger.info(f"   Latest Block: {network_status.get('latest_block', 'N/A')}")
            logger.info(f"   Current Slot: {network_status.get('current_slot', 'N/A')}")
            logger.info(f"   Protocol Version: {network_status.get('protocol_version', 'N/A')}")

            if network_status.get('connected'):
                logger.info("   ✅ Cardano network connection successful")
                return True
            else:
                logger.error("   ❌ Cardano network connection failed")
                return False

        except Exception as e:
            logger.error(f"   ❌ Network test failed: {e}")
            return False

    def test_wallet_info(self):
        """Test 2: Wallet configuration"""
        logger.info("🔑 Test 2: Cardano Wallet Configuration")

        try:
            wallet_info = self.cardano_service.get_wallet_info()

            if 'error' in wallet_info:
                logger.warning(f"   ⚠️  Wallet not configured: {wallet_info['error']}")
                return False

            logger.info(f"   Address: {wallet_info.get('address', 'N/A')}")
            logger.info(f"   ADA Balance: {wallet_info.get('ada_balance', 0):.6f} ADA")
            logger.info(f"   Network: {wallet_info.get('network', 'N/A')}")

            ada_balance = wallet_info.get('ada_balance', 0)

            if ada_balance > 1.0:  # Need ADA for transactions
                logger.info("   ✅ Sufficient ADA balance for transactions")
            else:
                logger.warning("   ⚠️  Low ADA balance, may not be able to send transactions")

            return True

        except Exception as e:
            logger.error(f"   ❌ Wallet test failed: {e}")
            return False
    
    def test_reward_calculations(self):
        """Test 3: Reward calculation logic"""
        logger.info("💰 Test 3: Cardano Reward Calculations")

        test_cases = [
            {"nimo_amount": 100, "confidence": 0.9, "contribution_type": "coding"},
            {"nimo_amount": 50, "confidence": 0.7, "contribution_type": "education"},
            {"nimo_amount": 75, "confidence": 0.85, "contribution_type": "volunteer"},
            {"nimo_amount": 25, "confidence": 0.6, "contribution_type": "community"},
            {"nimo_amount": 200, "confidence": 0.95, "contribution_type": "leadership"}
        ]

        for i, case in enumerate(test_cases, 1):
            try:
                calculation = self.unified_token_service.calculate_reward(
                    nimo_amount=case['nimo_amount'],
                    confidence=case['confidence'],
                    contribution_type=case['contribution_type']
                )

                logger.info(f"   Case {i}: {case['contribution_type']}")
                logger.info(f"      NIMO Tokens: {calculation.get('nimo_amount', case['nimo_amount'])}")
                logger.info(f"      ADA Reward: {calculation.get('ada_reward', 0):.6f} ADA")
                logger.info(f"      Confidence: {calculation.get('confidence', case['confidence']):.2f}")
                logger.info(f"      Total Value: ~${calculation.get('estimated_value_usd', 0):.3f}")

            except Exception as e:
                logger.error(f"   ❌ Case {i} failed: {e}")
                return False

        logger.info("   ✅ All reward calculations completed")
        return True
    
    def test_metta_integration(self):
        """Test 4: MeTTa reasoning integration"""
        logger.info("🧠 Test 4: MeTTa Integration with Cardano")

        # Test contribution scenarios
        test_contributions = [
            {
                "contribution_id": "test_1",
                "contribution_data": {
                    "user_id": "user1",
                    "category": "coding",
                    "title": "Smart Contract Development",
                    "evidence": [{"type": "github", "url": "https://github.com/test/repo"}]
                }
            },
            {
                "contribution_id": "test_2",
                "contribution_data": {
                    "user_id": "user2",
                    "category": "education",
                    "title": "Programming Tutorial",
                    "evidence": [{"type": "website", "url": "https://example.com/tutorial"}]
                }
            }
        ]

        for i, contrib in enumerate(test_contributions, 1):
            try:
                logger.info(f"   Testing contribution {i}: {contrib['contribution_data']['title']}")

                # Get MeTTa analysis
                metta_result = self.metta_integration.validate_contribution(
                    contrib['contribution_id'],
                    contrib['contribution_data']
                )

                logger.info(f"      Verified: {metta_result.get('verified')}")
                logger.info(f"      Confidence: {metta_result.get('confidence', 0):.2f}")
                logger.info(f"      Token Award: {metta_result.get('token_award', 0)}")
                logger.info(f"      Explanation: {metta_result.get('explanation', 'N/A')[:100]}...")

                # Calculate complete reward using Cardano service
                if metta_result.get('verified') and metta_result.get('token_award'):
                    reward_calc = self.unified_token_service.calculate_reward(
                        nimo_amount=metta_result['token_award'],
                        confidence=metta_result.get('confidence', 0),
                        contribution_type=contrib['contribution_data']['category']
                    )

                    logger.info(f"      ADA Reward: {reward_calc.get('ada_reward', 0):.6f} ADA")
                    logger.info(f"      Total Value: ~${reward_calc.get('estimated_value_usd', 0):.3f}")

            except Exception as e:
                logger.error(f"   ❌ MeTTa test {i} failed: {e}")
                return False

        logger.info("   ✅ MeTTa integration tests completed")
        return True
    
    def test_fee_estimation(self):
        """Test 5: Fee estimation for Cardano transactions"""
        logger.info("💰 Test 5: Cardano Fee Estimation")

        test_amounts = [1.0, 5.0, 10.0, 50.0]  # ADA amounts

        for amount in test_amounts:
            try:
                estimation = self.cardano_service.estimate_transaction_fee()
                if estimation.get('success'):
                    logger.info(f"   {amount:.1f} ADA Transaction:")
                    logger.info(f"      Estimated Fee: {estimation.get('estimated_fee_ada', 0):.6f} ADA")
                    logger.info(f"      Fee: {estimation.get('estimated_fee_lovelace', 0):,} lovelace")
                    logger.info(f"      Total Cost: {amount + estimation.get('estimated_fee_ada', 0):.6f} ADA")
                else:
                    logger.warning(f"   {amount:.1f} ADA: Fee estimation failed")

            except Exception as e:
                logger.error(f"   ❌ Fee estimation for {amount:.1f} ADA failed: {e}")
                return False

        logger.info("   ✅ Fee estimation tests completed")
        return True
    
    def test_blockchain_integration(self):
        """Test 6: Blockchain service integration"""
        logger.info("⛓️  Test 6: Blockchain Integration")
        
        if not self.blockchain_service:
            logger.warning("   ⚠️  Blockchain service not available, skipping")
            return True
        
        try:
            # Test blockchain connection
            connected = self.blockchain_service.is_connected()
            logger.info(f"   Blockchain Connected: {connected}")
            
            if connected:
                # Test network info
                network_info = self.blockchain_service.get_network_info()
                logger.info(f"   Network: {network_info.get('network')}")
                logger.info(f"   Latest Block: {network_info.get('latest_block')}")
                logger.info(f"   Gas Price: {network_info.get('current_gas_price_gwei'):.2f} gwei")
                
                # Test transaction cost estimation
                for operation in ['create_identity', 'verify_contribution']:
                    cost = self.blockchain_service.estimate_transaction_cost(operation)
                    if 'error' not in cost:
                        logger.info(f"   {operation}: {cost['total_cost_ada']:.6f} ADA")
                
                logger.info("   ✅ Blockchain integration working")
            else:
                logger.warning("   ⚠️  Blockchain not connected")
            
            return True
            
        except Exception as e:
            logger.error(f"   ❌ Blockchain integration test failed: {e}")
            return False
    
    def run_complete_test_suite(self):
        """Run all integration tests"""
        logger.info("🚀 Starting Complete USDC Integration Test Suite")
        logger.info("=" * 60)
        
        test_results = []
        
        # Run all tests
        tests = [
            ("Network Connection", self.test_network_connection),
            ("Service Account", self.test_service_account),
            ("Reward Calculations", self.test_reward_calculations),
            ("MeTTa Integration", self.test_metta_integration),
            ("Gas Estimation", self.test_gas_estimation),
            ("Blockchain Integration", self.test_blockchain_integration)
        ]
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                test_results.append((test_name, result))
                logger.info("")
            except Exception as e:
                logger.error(f"❌ {test_name} crashed: {e}")
                test_results.append((test_name, False))
                logger.info("")
        
        # Summary
        logger.info("📊 Test Results Summary")
        logger.info("=" * 60)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"   {status} {test_name}")
            if result:
                passed += 1
        
        logger.info("")
        logger.info(f"🏆 Overall: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("🎉 All tests passed! USDC integration is working correctly.")
        elif passed > total * 0.7:
            logger.info("⚠️  Most tests passed. Check failed tests and configuration.")
        else:
            logger.error("❌ Multiple tests failed. Check system configuration.")
        
        return passed, total

def main():
    """Main test execution"""
    try:
        tester = USDCIntegrationTester()
        passed, total = tester.run_complete_test_suite()
        
        if passed == total:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"🔥 Test suite crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()