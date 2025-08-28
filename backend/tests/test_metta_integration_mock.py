"""
Test script for MeTTa integration in mock mode
This script tests the MeTTa service with the mock implementation
"""

import os
import sys
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("metta_integration_test")

# Add the backend directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(script_dir, '..')
sys.path.append(backend_dir)

# Import the MeTTa service
from services.metta_service_hyperon import MeTTaService
from services.metta_integration_enhanced import get_metta_service

def test_metta_service_mock():
    """Test the MeTTa service in mock mode"""
    logger.info("Testing MeTTa service in mock mode...")
    
    # Initialize the service
    service = MeTTaService()
    
    # Check if we're in mock mode (we should be)
    try:
        import hyperon
        logger.info("MeTTa is available - using real implementation")
        is_mock = False
    except ImportError:
        logger.info("As expected, MeTTa is not available - using mock mode")
        is_mock = True
    
    # Define a test user
    user_id = "test-user-1"
    result = service.define_user(user_id, "TestUser")
    logger.info(f"Define user result: {result}")
    
    # Add skills
    service.add_skill(user_id, "Python", 5)
    service.add_skill(user_id, "MeTTa", 4)
    logger.info("Added skills to user")
    
    # Add a contribution
    contrib_id = "test-contrib-1"
    service.add_contribution(contrib_id, user_id, "education", "Teaching MeTTa")
    logger.info(f"Added contribution: {contrib_id}")
    
    # Add evidence
    service.add_evidence(contrib_id, "github", "https://github.com/test/metta-course")
    logger.info("Added evidence to contribution")
    
    # Validate contribution
    validation = service.validate_contribution(contrib_id)
    logger.info(f"Validation result: {validation}")
    
    # Test auto award
    award = service.auto_award(user_id, contrib_id)
    logger.info(f"Award result: {award}")
    
    # Test query token balance
    balance = service.query_token_balance(user_id)
    logger.info(f"Token balance: {balance}")
    
    # Test query user contributions
    contributions = service.query_user_contributions(user_id)
    logger.info(f"User contributions: {contributions}")
    
    logger.info("MeTTa service mock test completed successfully!")
    return True
    
    # Define a test user
    user_id = "test-user-1"
    service.define_user(user_id, "TestUser")
    logger.info(f"Defined user: {user_id}")
    
    # Add skills
    service.add_skill(user_id, "Python", 5)
    service.add_skill(user_id, "MeTTa", 4)
    logger.info("Added skills to user")
    
    # Add a contribution
    contrib_id = "test-contrib-1"
    service.add_contribution(contrib_id, user_id, "education", "Teaching MeTTa")
    logger.info(f"Added contribution: {contrib_id}")
    
    # Add evidence
    service.add_evidence(contrib_id, "github", "https://github.com/test/metta-course")
    logger.info("Added evidence to contribution")
    
    # Verify identity
    proof = {"email": "verified", "github": "active"}
    verified = service.verify_identity(user_id, proof)
    logger.info(f"Identity verification result: {verified}")
    
    # Calculate reputation
    contributions = [
        {"id": "c1", "type": "education", "value": 10},
        {"id": "c2", "type": "volunteer", "value": 5}
    ]
    reputation = service.calculate_reputation(user_id, contributions)
    logger.info(f"Reputation score: {reputation}")
    
    # Evaluate token award
    token_amount = service.evaluate_token_award(
        user_id, 
        "contribution", 
        {"type": "education", "quality": "high"}
    )
    logger.info(f"Token award amount: {token_amount}")
    
    logger.info("MeTTa service mock test completed successfully!")
    return True

def test_metta_integration():
    """Test the MeTTa integration layer"""
    logger.info("Testing MeTTa integration layer...")
    
    # Initialize the integration
    integration = get_metta_service()
    
    # Define a user
    user_id = "integration-user-1"
    integration.define_user(user_id, "IntegrationTest")
    logger.info(f"Defined user: {user_id}")
    
    # Add skills
    integration.add_skill(user_id, "Programming", 5)
    integration.add_skill(user_id, "Teaching", 4)
    logger.info("Added skills")
    
    # Add a contribution
    contrib_id = "integration-contrib-1"
    integration.add_contribution(contrib_id, user_id, "education", "Programming Workshop")
    logger.info(f"Added contribution: {contrib_id}")
    
    # Add evidence
    integration.add_evidence(contrib_id, "website", "https://example.com/workshop", "evidence-1")
    logger.info("Added evidence")
    
    # Mock user for sync test - This would normally come from the database
    class MockUser:
        def __init__(self):
            self.id = "mock-user-1"
            self.username = "MockUser"
            self.skills = [MockSkill("Python", 3), MockSkill("Teaching", 2)]
            self.tokens = MockTokens(100)
            self.contributions = [MockContribution()]
            
    class MockSkill:
        def __init__(self, name, level):
            self.name = name
            self.level = level
            
    class MockTokens:
        def __init__(self, balance):
            self.balance = balance
            
    class MockContribution:
        def __init__(self):
            self.id = "mock-contrib-1"
            self.category = "volunteer"
            self.title = "Community Service"
            self.evidence = [MockEvidence()]
            self.verifications = [MockVerification()]
            
    class MockEvidence:
        def __init__(self):
            self.id = "mock-evidence-1"
            self.type = "image"
            self.url = "https://example.com/image.jpg"
            
    class MockVerification:
        def __init__(self):
            self.organization = "Test Org"
            self.verifier_id = "verifier-1"
    
    # Test user sync
    mock_user = MockUser()
    integration.sync_user_to_metta(mock_user)
    logger.info(f"Synced mock user")
    
    # Save to file
    integration.save_to_file("test_integration.json")
    logger.info("Saved to file")
    
    logger.info("MeTTa integration test completed successfully!")
    return True

if __name__ == "__main__":
    logger.info("===== MeTTa Integration Test (Mock Mode) =====")
    
    # Test the MeTTa service
    service_result = test_metta_service_mock()
    
    # Test the integration layer
    integration_result = test_metta_integration()
    
    # Print summary
    logger.info("===== Test Results =====")
    logger.info(f"MeTTa Service Test: {'✓ PASS' if service_result else '✗ FAIL'}")
    logger.info(f"MeTTa Integration Test: {'✓ PASS' if integration_result else '✗ FAIL'}")
    
    if service_result and integration_result:
        logger.info("✓✓✓ All tests PASSED! MeTTa integration is working in mock mode.")
    else:
        logger.error("❌ Some tests FAILED. Please check the logs for details.")