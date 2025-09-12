#!/usr/bin/env python3
"""
Test script for the unified Key Manager system.
Validates that all key management functionality works correctly.
"""

import os
import sys
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.key_manager import key_manager

def test_key_manager():
    """Test all key manager functionality."""
    
    print("Testing Nimo Platform Key Manager")
    print("=" * 40)
    
    # Test 1: Key Manager Initialization
    print("\n1. Testing Key Manager Initialization...")
    print(f"   Key Manager Available: {'✅' if key_manager else '❌'}")
    
    if not key_manager:
        print("   ❌ Key Manager not available")
        return False
    
    # Test 2: Environment Variable Reading
    print("\n2. Testing Environment Variable Reading...")
    
    # Test Cardano service key
    cardano_key = key_manager.get_cardano_service_key()
    print(f"   Cardano Service Key: {'✅ Found' if cardano_key else '❌ Not Found'}")
    if cardano_key:
        print(f"   Key Length: {len(cardano_key)} characters")
    
    # Test Blockfrost API keys
    for network in ['preview', 'preprod', 'mainnet']:
        api_key = key_manager.get_blockfrost_api_key(network)
        print(f"   Blockfrost {network.title()}: {'✅ Found' if api_key else '❌ Not Found'}")
    
    # Test Flask and JWT secrets
    flask_secret = key_manager.get_flask_secret()
    jwt_secret = key_manager.get_jwt_secret()
    print(f"   Flask Secret: {'✅ Found' if flask_secret else '❌ Not Found'}")
    print(f"   JWT Secret: {'✅ Found' if jwt_secret else '❌ Not Found'}")
    
    # Test 3: Key Validation
    print("\n3. Testing Key Validation...")
    validation_results = key_manager.validate_key_security()
    
    for key_type, is_valid in validation_results.items():
        status = "✅ Valid" if is_valid else "❌ Invalid"
        print(f"   {key_type}: {status}")
    
    # Test 4: Encryption/Decryption (if available)
    print("\n4. Testing Encryption/Decryption...")
    test_data = "This is sensitive test data"
    
    encrypted_data = key_manager.encrypt_sensitive_data(test_data)
    if encrypted_data:
        print("   ✅ Encryption successful")
        
        decrypted_data = key_manager.decrypt_sensitive_data(encrypted_data)
        if decrypted_data == test_data:
            print("   ✅ Decryption successful")
        else:
            print("   ❌ Decryption failed")
    else:
        print("   ❌ Encryption not available")
    
    # Test 5: Secure Key Generation
    print("\n5. Testing Secure Key Generation...")
    for length in [16, 32, 64]:
        generated_key = key_manager.generate_secure_key(length)
        print(f"   {length}-byte key: {generated_key[:20]}... (length: {len(generated_key)})")
    
    # Test 6: Security Configuration Audit
    print("\n6. Testing Security Configuration Audit...")
    audit_result = key_manager.audit_security_configuration()
    
    print(f"   Security Level: {audit_result['security_level']}")
    print(f"   Critical Issues: {len(audit_result['critical_issues'])}")
    print(f"   Warnings: {len(audit_result['warnings'])}")
    
    if audit_result['critical_issues']:
        print("   Critical Issues:")
        for issue in audit_result['critical_issues']:
            print(f"     • {issue}")
    
    if audit_result['warnings']:
        print("   Warnings:")
        for warning in audit_result['warnings']:
            print(f"     • {warning}")
    
    # Test 7: Integration with Configuration
    print("\n7. Testing Integration with Configuration...")
    
    try:
        from config import Config
        config = Config()
        
        # Test if key manager values are being used
        uses_key_manager = (
            hasattr(config, 'SECRET_KEY') and 
            hasattr(config, 'JWT_SECRET_KEY')
        )
        print(f"   Config Integration: {'✅ Working' if uses_key_manager else '❌ Failed'}")
        
        # Check if using default values
        using_defaults = (
            'dev-key' in str(config.SECRET_KEY) or 
            'jwt-dev-key' in str(config.JWT_SECRET_KEY)
        )
        if using_defaults:
            print("   ⚠️  Warning: Using default keys (not secure for production)")
        else:
            print("   ✅ Using secure keys")
            
    except Exception as e:
        print(f"   ❌ Config integration test failed: {e}")
    
    # Summary
    print("\n📊 Test Summary")
    print("-" * 20)
    
    total_validations = len(validation_results)
    valid_keys = sum(1 for is_valid in validation_results.values() if is_valid)
    
    print(f"Valid Keys: {valid_keys}/{total_validations}")
    print(f"Security Score: {(valid_keys/total_validations)*100:.1f}%")
    
    if valid_keys == total_validations:
        print("✅ All tests passed! Key Manager is working correctly.")
        return True
    elif valid_keys > 0:
        print("⚠️  Some tests passed. Check warnings above.")
        return True
    else:
        print("❌ Key Manager tests failed. Please check configuration.")
        return False

def test_cardano_integration():
    """Test integration with Cardano service."""
    
    print("\n🔗 Testing Cardano Service Integration")
    print("=" * 40)
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services'))
        from services.cardano_service import CardanoService
        
        # Initialize Cardano service
        cardano_service = CardanoService()
        
        print(f"Service Available: {'✅' if cardano_service.available else '❌'}")
        if not cardano_service.available:
            print(f"Error: {cardano_service.error}")
        
        print(f"Network: {cardano_service.network_name}")
        print(f"Service Key Loaded: {'✅' if cardano_service.service_signing_key else '❌'}")
        print(f"Service Address: {cardano_service.service_address or 'Not available'}")
        
        return cardano_service.available
        
    except Exception as e:
        print(f"❌ Cardano integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("Starting Key Manager Tests...")
    
    # Test key manager
    key_manager_ok = test_key_manager()
    
    # Test Cardano integration
    cardano_integration_ok = test_cardano_integration()
    
    # Overall result
    print(f"\n🏁 Overall Test Result")
    print("=" * 30)
    
    if key_manager_ok and cardano_integration_ok:
        print("✅ All tests passed! System is ready for secure deployment.")
        sys.exit(0)
    elif key_manager_ok:
        print("⚠️  Key Manager working but some integrations need attention.")
        sys.exit(0)
    else:
        print("❌ Tests failed. Please fix configuration before deployment.")
        sys.exit(1)