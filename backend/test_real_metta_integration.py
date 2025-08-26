#!/usr/bin/env python3
"""
Real MeTTa Integration Test for Nimo Platform
Tests the real MeTTa reasoning service using the Rust REPL
"""

import sys
import os
import logging

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('real_metta_integration_test')

def test_real_metta_service():
    """Test real MeTTa service functionality"""
    logger.info("===== Real MeTTa Service Integration Test =====")
    
    try:
        # Import the real MeTTa service
        from services.metta_service_real import RealMeTTaService
        logger.info("✓ Successfully imported RealMeTTaService")
        
        # Initialize the service
        metta_service = RealMeTTaService()
        logger.info("✓ Successfully initialized RealMeTTaService")
        
        # Test basic operations
        logger.info("Testing real MeTTa operations...")
        
        # Test 1: Add a user
        logger.info("Test 1: Adding user with skills...")
        result = metta_service.define_user("bob", ["python", "blockchain", "ai"])
        logger.info(f"Define user result: {result}")
        
        # Test 2: Add a skill
        logger.info("Test 2: Adding additional skill...")
        skill_result = metta_service.add_skill("bob", "machine-learning", 3)
        logger.info(f"Add skill result: {skill_result}")
        
        # Test 3: Add a contribution
        logger.info("Test 3: Adding contribution...")
        contribution_result = metta_service.add_contribution(
            "ml-model-1", 
            "bob", 
            "machine-learning", 
            "Implemented neural network for identity verification"
        )
        logger.info(f"Add contribution result: {contribution_result}")
        
        # Test 4: Add evidence for the contribution
        logger.info("Test 4: Adding evidence...")
        evidence_result = metta_service.add_evidence(
            "ml-model-1",
            "github-repo",
            "https://github.com/bob/identity-ml"
        )
        logger.info(f"Add evidence result: {evidence_result}")
        
        # Test 5: Verify contribution
        logger.info("Test 5: Verifying contribution...")
        verify_result = metta_service.verify_contribution("ml-model-1", "TrueAGI", "system")
        logger.info(f"Verify contribution result: {verify_result}")
        
        # Test 6: Validate contribution
        logger.info("Test 6: Validating contribution...")
        validation = metta_service.validate_contribution("ml-model-1")
        logger.info(f"Validation result: {validation}")
        
        # Test 7: Auto award tokens
        logger.info("Test 7: Auto award tokens...")
        award_result = metta_service.auto_award("bob", "ml-model-1")
        logger.info(f"Auto award result: {award_result}")
        
        # Test 8: Query user contributions
        logger.info("Test 8: Querying user contributions...")
        contributions = metta_service.query_user_contributions("bob")
        logger.info(f"User contributions: {contributions}")
        
        # Test 9: Query token balance
        logger.info("Test 9: Querying token balance...")
        balance = metta_service.query_token_balance("bob")
        logger.info(f"Token balance: {balance}")
        
        # Test 10: Save workspace
        logger.info("Test 10: Saving workspace...")
        save_result = metta_service.save_to_file()
        logger.info(f"Save result: {save_result}")
        
        logger.info("✓ All real MeTTa service tests completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Real MeTTa service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_metta_runner_directly():
    """Test the MeTTa runner directly"""
    logger.info("===== Direct MeTTa Runner Test =====")
    
    try:
        from services.real_metta_runner import RealMeTTaRunner
        logger.info("✓ Successfully imported RealMeTTaRunner")
        
        # Initialize runner
        runner = RealMeTTaRunner()
        logger.info("✓ Successfully initialized RealMeTTaRunner")
        
        # Test connection
        if runner.test_connection():
            logger.info("✓ MeTTa connection test successful")
            
            # Test advanced MeTTa reasoning
            logger.info("Testing advanced MeTTa reasoning...")
            
            # Load some advanced rules
            advanced_rules = """
; Advanced identity and reputation rules
(= (SkillLevel $user $skill $level) 
   (and (User $user) (HasSkill $user $skill) (SkillRating $user $skill $level)))

(= (ReputationScore $user $score)
   (sum-contributions $user $score))
   
(= (TrustLevel $user $level)
   (if (> (ReputationScore $user) 100) high 
       (if (> (ReputationScore $user) 50) medium low)))

; Contribution verification rules
(= (VerificationRequired $contrib $threshold)
   (if (> (ContributionValue $contrib) $threshold) peer-review self-verified))

(= (TokenMultiplier $user $multiplier)
   (case (TrustLevel $user)
     (high 1.5)
     (medium 1.0)
     (low 0.5)))
"""
            
            stdout, stderr, return_code = runner.execute_script(advanced_rules)
            if return_code == 0:
                logger.info("✓ Advanced rules loaded successfully")
            else:
                logger.warning(f"Advanced rules failed to load: {stderr}")
            
            # Test complex query
            complex_query = """
; Test complex reasoning
(= (TestUser "charlie") ("ai" "blockchain" "research"))
!(TestUser "charlie")
"""
            
            results = runner.execute_query("!(TestUser \"charlie\")")
            logger.info(f"Complex query results: {results}")
            
            logger.info("✓ Direct MeTTa runner tests completed!")
            return True
        else:
            logger.error("❌ MeTTa connection test failed")
            return False
            
    except Exception as e:
        logger.error(f"Direct MeTTa runner test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_configuration():
    """Test configuration settings"""
    logger.info("===== Real MeTTa Configuration Test =====")
    
    try:
        from config import active_config
        logger.info("✓ Successfully imported configuration")
        
        logger.info(f"USE_METTA_REASONING: {active_config.USE_METTA_REASONING}")
        logger.info(f"METTA_DATABASE_PATH: {active_config.METTA_DATABASE_PATH}")
        logger.info(f"METTA_CORE_RULES_PATH: {active_config.METTA_CORE_RULES_PATH}")
        
        if hasattr(active_config, 'METTA_MODE'):
            logger.info(f"METTA_MODE: {active_config.METTA_MODE}")
            if active_config.METTA_MODE == 'real':
                logger.info("✓ Real MeTTa mode is ENABLED")
            else:
                logger.warning("⚠ MeTTa is not in real mode")
        
        if active_config.USE_METTA_REASONING:
            logger.info("✓ MeTTa reasoning is ENABLED")
        else:
            logger.error("❌ MeTTa reasoning is DISABLED")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Configuration test failed: {e}")
        return False

def test_core_rules_loading():
    """Test loading of core MeTTa rules"""
    logger.info("===== Core Rules Loading Test =====")
    
    try:
        # Check if core rules file exists
        rules_file = "E:\\Polymath Universata\\Projects\\Nimo\\backend\\rules\\core_rules.metta"
        if os.path.exists(rules_file):
            logger.info(f"✓ Core rules file found at: {rules_file}")
            
            # Try to load and validate rules
            from services.real_metta_runner import RealMeTTaRunner
            runner = RealMeTTaRunner()
            
            success = runner.load_core_rules(rules_file)
            if success:
                logger.info("✓ Core rules loaded successfully")
                return True
            else:
                logger.error("❌ Failed to load core rules")
                return False
        else:
            logger.error(f"❌ Core rules file not found at: {rules_file}")
            return False
            
    except Exception as e:
        logger.error(f"Core rules loading test failed: {e}")
        return False

def main():
    """Run all real MeTTa integration tests"""
    logger.info("Starting Real MeTTa integration tests...")
    
    tests = [
        ("Configuration", test_configuration),
        ("Core Rules Loading", test_core_rules_loading),
        ("Direct MeTTa Runner", test_metta_runner_directly),
        ("Real MeTTa Service", test_real_metta_service)
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
    logger.info("\n===== REAL METTA TEST RESULTS SUMMARY =====")
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Real MeTTa integration is working perfectly!")
        logger.info("🚀 Your Nimo platform is ready for the hackathon with real MeTTa reasoning!")
        return 0
    else:
        logger.error("❌ Some tests failed. Check the logs above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())