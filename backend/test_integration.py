#!/usr/bin/env python3
"""
Integration test for MeTTa service in Nimo platform
Tests the MeTTa reasoning service with mock mode
"""

import sys
import os
import logging

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('metta_integration_test')

def test_metta_service():
    """Test MeTTa service functionality"""
    logger.info("===== MeTTa Service Integration Test =====")
    
    try:
        # Import the MeTTa service
        from services.metta_service_hyperon import MeTTaService
        logger.info("✓ Successfully imported MeTTaService")
        
        # Initialize the service
        metta_service = MeTTaService()
        logger.info("✓ Successfully initialized MeTTaService")
        
        # Test basic operations
        logger.info("Testing basic MeTTa operations...")
        
        # Test 1: Add a user
        logger.info("Test 1: Adding user...")
        result = metta_service.define_user("alice", ["python", "blockchain"])
        logger.info(f"Define user result: {result}")
        
        # Test 2: Add a contribution
        logger.info("Test 2: Adding contribution...")
        contribution_result = metta_service.add_contribution("alice", "implemented smart contract", ["blockchain", "solidity"])
        logger.info(f"Add contribution result: {contribution_result}")
        
        # Test 3: Verify contribution
        logger.info("Test 3: Verifying contribution...")
        verify_result = metta_service.verify_contribution("alice", "implemented smart contract")
        logger.info(f"Verify contribution result: {verify_result}")
        
        # Test 4: Auto award tokens
        logger.info("Test 4: Auto award tokens...")
        award_result = metta_service.auto_award("alice", "implemented smart contract")
        logger.info(f"Auto award result: {award_result}")
        
        # Test 5: Query user contributions
        logger.info("Test 5: Querying user contributions...")
        query_result = metta_service.query_user_contributions("alice")
        logger.info(f"Query result: {query_result}")
        
        # Test 6: Query token balance
        logger.info("Test 6: Querying token balance...")
        balance_result = metta_service.query_token_balance("alice")
        logger.info(f"Balance result: {balance_result}")
        
        logger.info("✓ All MeTTa service tests completed successfully!")
        return True
        
    except ImportError as e:
        logger.error(f"Failed to import MeTTaService: {e}")
        return False
    except Exception as e:
        logger.error(f"MeTTa service test failed: {e}")
        return False

def test_metta_reasoning():
    """Test MeTTa reasoning functionality"""
    logger.info("===== MeTTa Reasoning Test =====")
    
    try:
        from services import metta_reasoning
        logger.info("✓ Successfully imported metta_reasoning module")
        
        # Test reasoning functions
        if hasattr(metta_reasoning, 'verify_contribution_with_metta'):
            logger.info("Testing contribution verification...")
            result = metta_reasoning.verify_contribution_with_metta(
                user_id="alice",
                contribution_data={
                    "title": "Smart Contract Implementation",
                    "description": "Implemented ERC20 token contract",
                    "skills": ["blockchain", "solidity"]
                }
            )
            logger.info(f"Verification result: {result}")
        
        logger.info("✓ MeTTa reasoning tests completed!")
        return True
        
    except ImportError as e:
        logger.error(f"Failed to import metta_reasoning: {e}")
        return False
    except Exception as e:
        logger.error(f"MeTTa reasoning test failed: {e}")
        return False

def test_configuration():
    """Test configuration settings"""
    logger.info("===== Configuration Test =====")
    
    try:
        from config import active_config
        logger.info("✓ Successfully imported configuration")
        
        logger.info(f"USE_METTA_REASONING: {active_config.USE_METTA_REASONING}")
        logger.info(f"METTA_DATABASE_PATH: {active_config.METTA_DATABASE_PATH}")
        logger.info(f"METTA_CORE_RULES_PATH: {active_config.METTA_CORE_RULES_PATH}")
        
        if hasattr(active_config, 'METTA_MODE'):
            logger.info(f"METTA_MODE: {active_config.METTA_MODE}")
        
        if active_config.USE_METTA_REASONING:
            logger.info("✓ MeTTa reasoning is ENABLED")
        else:
            logger.warning("⚠ MeTTa reasoning is DISABLED")
            
        return True
        
    except Exception as e:
        logger.error(f"Configuration test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    logger.info("Starting MeTTa integration tests...")
    
    tests = [
        ("Configuration", test_configuration),
        ("MeTTa Service", test_metta_service),
        ("MeTTa Reasoning", test_metta_reasoning)
    ]
    
    results = {}
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} Test ---")
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"{test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n===== TEST RESULTS SUMMARY =====")
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! MeTTa integration is working.")
        return 0
    else:
        logger.error("❌ Some tests failed. Check the logs above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())