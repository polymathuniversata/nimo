#!/usr/bin/env python3
"""
Test USDC Integration with MeTTa Rewards System

This script tests the complete flow of MeTTa reasoning → NIMO tokens → USDC rewards
"""

import sys
import os
import json
import logging
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from services.usdc_integration import USDCIntegration
from services.metta_integration import MeTTaIntegration
from services.metta_blockchain_bridge import MeTTaBlockchainBridge
from services.blockchain_service import BlockchainService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class USDCIntegrationTester:
    def __init__(self):
        """Initialize test environment"""
        self.usdc_integration = USDCIntegration()
        self.metta_integration = MeTTaIntegration()
        
        # Try to initialize blockchain service (will gracefully fail if not configured)
        try:
            self.blockchain_service = BlockchainService()
            self.bridge = MeTTaBlockchainBridge(self.metta_integration, self.blockchain_service)
        except Exception as e:
            logger.warning(f"Blockchain service not available: {e}")
            self.blockchain_service = None
            self.bridge = None
    
    def test_network_connection(self):
        """Test 1: Network connection and status"""
        logger.info("🌐 Test 1: Network Connection")
        
        try:
            network_status = self.usdc_integration.get_network_status()
            logger.info(f"   Network: {network_status.get('network')}")
            logger.info(f"   Connected: {network_status.get('connected')}")
            logger.info(f"   Chain ID: {network_status.get('chain_id')}")
            logger.info(f"   Latest Block: {network_status.get('latest_block')}")
            logger.info(f"   Gas Price: {network_status.get('gas_price_gwei'):.2f} gwei")
            logger.info(f"   USDC Contract: {network_status.get('usdc_contract')}")
            logger.info(f"   USDC Enabled: {network_status.get('usdc_enabled')}")
            
            if network_status.get('connected'):
                logger.info("   ✅ Network connection successful")
                return True
            else:
                logger.error("   ❌ Network connection failed")
                return False
                
        except Exception as e:
            logger.error(f"   ❌ Network test failed: {e}")
            return False
    
    def test_service_account(self):
        """Test 2: Service account configuration"""
        logger.info("🔑 Test 2: Service Account")
        
        try:
            account_info = self.usdc_integration.get_service_account_info()
            
            if 'error' in account_info:
                logger.warning(f"   ⚠️  Service account not configured: {account_info['error']}")
                return False
            
            logger.info(f"   Address: {account_info.get('address')}")
            logger.info(f"   ETH Balance: {account_info.get('eth_balance'):.4f} ETH")
            logger.info(f"   USDC Balance: {account_info.get('usdc_balance'):.2f} USDC")
            
            eth_balance = account_info.get('eth_balance', 0)
            usdc_balance = account_info.get('usdc_balance', 0)
            
            if eth_balance > 0.001:  # Need ETH for gas
                logger.info("   ✅ Sufficient ETH balance for gas")
            else:
                logger.warning("   ⚠️  Low ETH balance, may not be able to send transactions")
            
            if usdc_balance > 0:
                logger.info("   ✅ USDC balance available for rewards")
            else:
                logger.warning("   ⚠️  No USDC balance, cannot send rewards")
            
            return True
            
        except Exception as e:
            logger.error(f"   ❌ Service account test failed: {e}")
            return False
    
    def test_reward_calculations(self):
        """Test 3: Reward calculation logic"""
        logger.info("💰 Test 3: Reward Calculations")
        
        test_cases = [
            {"nimo_amount": 100, "confidence": 0.9, "contribution_type": "coding"},
            {"nimo_amount": 50, "confidence": 0.7, "contribution_type": "education"},
            {"nimo_amount": 75, "confidence": 0.85, "contribution_type": "volunteer"},
            {"nimo_amount": 25, "confidence": 0.6, "contribution_type": "community"},
            {"nimo_amount": 200, "confidence": 0.95, "contribution_type": "leadership"}
        ]
        
        for i, case in enumerate(test_cases, 1):
            try:
                calculation = self.usdc_integration.get_reward_calculation(
                    nimo_amount=case['nimo_amount'],
                    confidence=case['confidence'],
                    contribution_type=case['contribution_type']
                )
                
                logger.info(f"   Case {i}: {case['contribution_type']}")
                logger.info(f"      NIMO Tokens: {calculation['nimo_amount']}")
                logger.info(f"      Base USDC: ${calculation['base_usdc_amount']:.3f}")
                logger.info(f"      Confidence: {calculation['confidence']:.2f}")
                logger.info(f"      Multiplier: {calculation['confidence_multiplier']:.2f}x")
                logger.info(f"      Final USDC: ${calculation['final_usdc_amount']:.3f}")
                logger.info(f"      Pays USDC: {calculation['pays_usdc']}")
                
            except Exception as e:
                logger.error(f"   ❌ Case {i} failed: {e}")
                return False
        
        logger.info("   ✅ All reward calculations completed")
        return True
    
    def test_metta_integration(self):
        """Test 4: MeTTa reasoning integration"""
        logger.info("🧠 Test 4: MeTTa Integration")
        
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
                
                # Calculate complete reward
                if metta_result.get('verified') and metta_result.get('token_award'):
                    usdc_calc = self.usdc_integration.get_reward_calculation(
                        nimo_amount=metta_result['token_award'],
                        confidence=metta_result.get('confidence', 0),
                        contribution_type=contrib['contribution_data']['category']
                    )
                    
                    logger.info(f"      USDC Reward: ${usdc_calc['final_usdc_amount']:.3f}")
                    logger.info(f"      Total Value: ~${usdc_calc['final_usdc_amount'] + (metta_result['token_award'] * 0.01):.3f}")
                
            except Exception as e:
                logger.error(f"   ❌ MeTTa test {i} failed: {e}")
                return False
        
        logger.info("   ✅ MeTTa integration tests completed")
        return True
    
    def test_gas_estimation(self):
        """Test 5: Gas estimation for USDC transfers"""
        logger.info("⛽ Test 5: Gas Estimation")
        
        test_address = "0x742d35Cc6634C0532925a3b8D6AC14"  # Sample address
        test_amounts = [0.01, 0.50, 1.00, 5.00]
        
        for amount in test_amounts:
            try:
                from decimal import Decimal
                estimation = self.usdc_integration.estimate_gas_for_transfer(
                    to_address=test_address,
                    usdc_amount=Decimal(str(amount))
                )
                
                if 'error' in estimation:
                    logger.warning(f"   ${amount:.2f}: {estimation['error']}")
                else:
                    logger.info(f"   ${amount:.2f} USDC:")
                    logger.info(f"      Gas: {estimation['gas_estimate']:,}")
                    logger.info(f"      Cost: {estimation['total_gas_cost_eth']:.6f} ETH")
                    logger.info(f"      Gas Price: {estimation['gas_price_gwei']:.2f} gwei")
                
            except Exception as e:
                logger.error(f"   ❌ Gas estimation for ${amount:.2f} failed: {e}")
                return False
        
        logger.info("   ✅ Gas estimation tests completed")
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
                        logger.info(f"   {operation}: {cost['total_cost_eth']:.6f} ETH")
                
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