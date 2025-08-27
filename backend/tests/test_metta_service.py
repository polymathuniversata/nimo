"""
Test script for the simplified MeTTa service.

This script tests the MeTTa service with a focus on
persistence, contribution validation, and token awards.
"""

import os
import sys
import json
import shutil
from pathlib import Path

# Add the parent directory to sys.path to import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.metta_service_simplified import MeTTaService

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "test_data"

def setup_test_environment():
    """Set up test environment"""
    print("\n--- Setting up test environment ---")
    
    # Create test data directory if it doesn't exist
    TEST_DATA_DIR.mkdir(exist_ok=True)
    
    # Clean up any previous test data
    db_path = TEST_DATA_DIR / "test_metta_space.json"
    if db_path.exists():
        db_path.unlink()
    
    return db_path

def teardown_test_environment():
    """Clean up after tests"""
    print("\n--- Cleaning up test environment ---")
    
    # Remove test data directory
    if TEST_DATA_DIR.exists():
        shutil.rmtree(TEST_DATA_DIR)

def test_service_initialization():
    """Test service initialization"""
    print("\n--- Testing service initialization ---")
    
    db_path = setup_test_environment()
    service = MeTTaService(db_path=str(db_path))
    
    # Check if service was initialized
    assert service is not None
    assert service.db_path == str(db_path)
    
    return True

def test_user_management():
    """Test user management"""
    print("\n--- Testing user management ---")
    
    db_path = setup_test_environment()
    service = MeTTaService(db_path=str(db_path))
    
    # Define a user
    result = service.define_user("test-user-1", "TestUser")
    print(f"Define user result: {result}")
    
    # Add skills
    service.add_skill("test-user-1", "Python", 5)
    service.add_skill("test-user-1", "JavaScript", 3)
    
    # Set token balance
    service.set_token_balance("test-user-1", 100)
    
    # Save to file
    service.save_to_file()
    
    # Check if file was created
    assert db_path.exists()
    
    # Create a new service and load from file
    new_service = MeTTaService(db_path=str(db_path))
    new_service.load_from_file()
    
    # Check token balance
    balance = new_service.query_token_balance("test-user-1")
    print(f"Token balance: {balance}")
    
    return balance == 100

def test_contribution_workflow():
    """Test contribution workflow"""
    print("\n--- Testing contribution workflow ---")
    
    db_path = setup_test_environment()
    service = MeTTaService(db_path=str(db_path))
    
    # Define a user
    service.define_user("test-user-2", "ContribUser")
    service.add_skill("test-user-2", "Coding", 4)
    service.set_token_balance("test-user-2", 50)
    
    # Add a contribution
    service.add_contribution("test-contrib-1", "test-user-2", "coding", "Test Project")
    
    # Add evidence
    service.add_evidence("test-contrib-1", "github", "https://github.com/test/project")
    
    # Validate contribution (should be valid)
    validation = service.validate_contribution("test-contrib-1")
    print(f"Validation result: {validation}")
    
    # Check if validation was successful
    assert validation["valid"]
    
    # Auto award tokens
    award = service.auto_award("test-user-2", "test-contrib-1")
    print(f"Award result: {award}")
    
    # Check if award was successful
    assert award["success"]
    assert award["new_balance"] == 125  # 50 + 75
    
    # Save to file
    service.save_to_file()
    
    # Check file content
    with open(db_path, 'r') as f:
        data = json.load(f)
        assert "atoms" in data
        assert len(data["atoms"]) >= 5  # User, HasSkill, Contribution, Evidence, TokenBalance
    
    return True

def test_contribution_validation():
    """Test contribution validation logic"""
    print("\n--- Testing contribution validation ---")
    
    db_path = setup_test_environment()
    service = MeTTaService(db_path=str(db_path))
    
    # Define a user
    service.define_user("test-user-3", "ValidUser")
    service.add_skill("test-user-3", "Coding", 3)
    
    # Add a contribution (no evidence)
    service.add_contribution("invalid-contrib", "test-user-3", "coding", "Invalid Project")
    
    # Validate contribution (should be invalid without evidence)
    validation = service.validate_contribution("invalid-contrib")
    print(f"Invalid contribution validation: {validation}")
    assert not validation["valid"]
    
    # Add evidence to make it valid
    service.add_evidence("invalid-contrib", "github", "https://github.com/test/project")
    
    # Validate again (should be valid now)
    validation = service.validate_contribution("invalid-contrib")
    print(f"Valid contribution validation: {validation}")
    assert validation["valid"]
    
    return True

def test_persistence():
    """Test persistence"""
    print("\n--- Testing persistence ---")
    
    db_path = setup_test_environment()
    service = MeTTaService(db_path=str(db_path))
    
    # Define user and add contributions
    service.define_user("persist-user", "PersistUser")
    service.add_skill("persist-user", "Testing", 5)
    service.add_contribution("persist-contrib", "persist-user", "testing", "Persistence Test")
    service.add_evidence("persist-contrib", "github", "https://github.com/test/persist")
    service.set_token_balance("persist-user", 200)
    
    # Save to file
    service.save_to_file()
    
    # Create a new service and load from file
    new_service = MeTTaService(db_path=str(db_path))
    new_service.load_from_file()
    
    # Query contributions
    contributions = new_service.query_user_contributions("persist-user")
    print(f"User contributions: {contributions}")
    
    # Check balance
    balance = new_service.query_token_balance("persist-user")
    print(f"User balance: {balance}")
    
    return "persist-contrib" in contributions and balance == 200

def run_all_tests():
    """Run all tests and report results"""
    tests = [
        test_service_initialization,
        test_user_management,
        test_contribution_workflow,
        test_contribution_validation,
        test_persistence
    ]
    
    results = []
    
    print("\n=== RUNNING METTA SERVICE TESTS ===\n")
    
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
            print(f"Test {test.__name__}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            results.append((test.__name__, False))
            print(f"Test {test.__name__}: ERROR - {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Print summary
    print("\n=== TEST SUMMARY ===")
    passed = sum(1 for _, r in results if r)
    failed = sum(1 for _, r in results if not r)
    print(f"Passed: {passed}/{len(results)}")
    print(f"Failed: {failed}/{len(results)}")
    
    # Print failed tests
    if failed > 0:
        print("\nFailed tests:")
        for name, result in results:
            if not result:
                print(f"- {name}")
    
    # Clean up
    teardown_test_environment()
    
    return passed == len(results)

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)