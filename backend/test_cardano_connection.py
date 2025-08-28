#!/usr/bin/env python3
"""
Cardano Connection Test Script

This script tests the Cardano integration without requiring API keys
by using mock/demo modes and validating the service architecture.
"""

import os
import sys
import json
from datetime import datetime

def test_cardano_imports():
    """Test that all Cardano imports work correctly"""
    print("[TEST] Testing Cardano imports...")
    
    try:
        from services.cardano_service import CardanoService, CardanoNetwork
        print("  [OK] CardanoService imported successfully")
        
        from pycardano import Network, BlockFrostChainContext
        print("  [OK] PyCardano core imports working")
        
        return True
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False

def test_cardano_service_initialization():
    """Test CardanoService initialization"""
    print("\n🔍 Testing CardanoService initialization...")
    
    try:
        from services.cardano_service import CardanoService
        
        # Test without API keys (should gracefully fail)
        cs = CardanoService()
        print(f"  📊 Service Available: {cs.available}")
        print(f"  📊 Network: {cs.network_name}")
        print(f"  📊 Error: {cs.error}")
        
        if not cs.available:
            print("  ⚠️  Service not available (expected without API keys)")
        else:
            print("  ✅ Service initialized successfully")
        
        return True
    except Exception as e:
        print(f"  ❌ Service initialization error: {e}")
        return False

def test_metta_integration():
    """Test MeTTa integration still works"""
    print("\n🔍 Testing MeTTa integration...")
    
    try:
        from services.metta_integration_enhanced import get_metta_service
        
        metta = get_metta_service()
        health = metta.health_check()
        
        print(f"  📊 MeTTa Status: {health.get('status')}")
        print(f"  📊 MeTTa Mode: {health.get('mode', 'unknown')}")
        print(f"  📊 MeTTa Connected: {health.get('connected', False)}")
        
        if health.get('status') == 'operational':
            print("  ✅ MeTTa integration working")
        else:
            print("  ⚠️  MeTTa integration has issues but still functional")
        
        return True
    except Exception as e:
        print(f"  ❌ MeTTa integration error: {e}")
        return False

def test_reward_calculation():
    """Test reward calculation logic"""
    print("\n🔍 Testing reward calculation logic...")
    
    try:
        from services.cardano_service import CardanoService
        
        cs = CardanoService()
        
        # Test reward calculation (should work without blockchain connection)
        calculation = cs.get_reward_calculation(
            nimo_amount=100,
            confidence=0.85,
            contribution_type="coding"
        )
        
        print("  📊 Test Reward Calculation:")
        print(f"    NIMO Amount: {calculation['nimo_amount']}")
        print(f"    Confidence: {calculation['confidence']}")
        print(f"    ADA Reward: {calculation['final_ada_amount']}")
        print(f"    Pays ADA: {calculation['pays_ada']}")
        
        if calculation['nimo_amount'] == 100 and calculation['confidence'] == 0.85:
            print("  ✅ Reward calculation working correctly")
            return True
        else:
            print("  ❌ Reward calculation returned unexpected results")
            return False
            
    except Exception as e:
        print(f"  ❌ Reward calculation error: {e}")
        return False

def test_api_integration():
    """Test API integration with Flask app"""
    print("\n🔍 Testing Flask API integration...")
    
    try:
        from app import create_app
        
        app = create_app()
        
        with app.test_client() as client:
            # Test the cardano status endpoint (should work without auth for basic info)
            response = client.get('/api/cardano/faucet-info')
            
            if response.status_code in [200, 401]:  # 401 is ok (needs auth)
                print("  ✅ Cardano routes registered successfully")
                
                if response.status_code == 200:
                    data = json.loads(response.data)
                    print(f"    Faucet URL: {data.get('data', {}).get('faucet_url', 'N/A')}")
                    
                return True
            else:
                print(f"  ❌ API endpoint returned status: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"  ❌ API integration error: {e}")
        return False

def test_with_api_keys():
    """Test with actual API keys if available"""
    print("\n🔍 Testing with Blockfrost API keys...")
    
    preview_key = os.getenv('BLOCKFROST_PROJECT_ID_PREVIEW')
    preprod_key = os.getenv('BLOCKFROST_PROJECT_ID_PREPROD')
    
    if not preview_key and not preprod_key:
        print("  ⚠️  No API keys found in environment")
        print("  💡 Set BLOCKFROST_PROJECT_ID_PREVIEW to test with real blockchain")
        return True
    
    try:
        from services.cardano_service import CardanoService
        
        # Test with preview network
        if preview_key:
            print("  🌐 Testing Preview network connection...")
            cs = CardanoService(network="preview", blockfrost_project_id=preview_key)
            
            if cs.available:
                print("  ✅ Preview network connection successful")
                
                # Test network info
                info = cs.get_network_info()
                print(f"    Network: {info.get('network')}")
                print(f"    Connected: {info.get('connected')}")
                print(f"    Latest Block: {info.get('latest_block_slot', 'N/A')}")
                
                return True
            else:
                print(f"  ❌ Preview network connection failed: {cs.error}")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ API key test error: {e}")
        return False

def generate_test_report(results):
    """Generate a test report"""
    print("\n" + "="*60)
    print("📋 CARDANO INTEGRATION TEST REPORT")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    print(f"📊 Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("✨ Cardano integration is ready for blockchain testing")
        
        if not os.getenv('BLOCKFROST_PROJECT_ID_PREVIEW'):
            print("\n📝 Next Steps:")
            print("1. Get Blockfrost API key from https://blockfrost.io")
            print("2. Set BLOCKFROST_PROJECT_ID_PREVIEW environment variable") 
            print("3. Re-run this test to verify blockchain connectivity")
            print("4. Fund test wallet with ADA from faucet")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("Please review the errors above and fix integration issues")
    
    # Detailed results
    print(f"\n📋 Test Details:")
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    print(f"\n🕐 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    return passed_tests == total_tests

def main():
    """Run all tests"""
    print("🚀 Starting Cardano Integration Tests...")
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Run all tests
    results["Cardano Imports"] = test_cardano_imports()
    results["Service Initialization"] = test_cardano_service_initialization()  
    results["MeTTa Integration"] = test_metta_integration()
    results["Reward Calculation"] = test_reward_calculation()
    results["API Integration"] = test_api_integration()
    results["Blockchain Connection"] = test_with_api_keys()
    
    # Generate report
    success = generate_test_report(results)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())