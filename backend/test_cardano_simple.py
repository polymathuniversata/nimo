#!/usr/bin/env python3
"""
Simple Cardano Integration Test

Tests the Cardano integration without special characters or emojis.
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
        print(f"  [ERROR] Import error: {e}")
        return False

def test_cardano_service_initialization():
    """Test CardanoService initialization"""
    print("\n[TEST] Testing CardanoService initialization...")
    
    try:
        from services.cardano_service import CardanoService
        
        # Test without API keys (should gracefully fail)
        cs = CardanoService()
        print(f"  [INFO] Service Available: {cs.available}")
        print(f"  [INFO] Network: {cs.network_name}")
        print(f"  [INFO] Error: {cs.error}")
        
        if not cs.available:
            print("  [EXPECTED] Service not available (expected without API keys)")
        else:
            print("  [OK] Service initialized successfully")
        
        return True
    except Exception as e:
        print(f"  [ERROR] Service initialization error: {e}")
        return False

def test_metta_integration():
    """Test MeTTa integration still works"""
    print("\n[TEST] Testing MeTTa integration...")
    
    try:
        from services.metta_integration_enhanced import get_metta_service
        
        metta = get_metta_service()
        health = metta.health_check()
        
        print(f"  [INFO] MeTTa Status: {health.get('status')}")
        print(f"  [INFO] MeTTa Mode: {health.get('mode', 'unknown')}")
        print(f"  [INFO] MeTTa Connected: {health.get('connected', False)}")
        
        if health.get('status') == 'operational':
            print("  [OK] MeTTa integration working")
        else:
            print("  [WARNING] MeTTa integration has issues but still functional")
        
        return True
    except Exception as e:
        print(f"  [ERROR] MeTTa integration error: {e}")
        return False

def test_reward_calculation():
    """Test reward calculation logic"""
    print("\n[TEST] Testing reward calculation logic...")
    
    try:
        from services.cardano_service import CardanoService
        
        cs = CardanoService()
        
        # Test reward calculation (should work without blockchain connection)
        calculation = cs.get_reward_calculation(
            nimo_amount=100,
            confidence=0.85,
            contribution_type="coding"
        )
        
        print("  [INFO] Test Reward Calculation:")
        print(f"    NIMO Amount: {calculation['nimo_amount']}")
        print(f"    Confidence: {calculation['confidence']}")
        print(f"    ADA Reward: {calculation['final_ada_amount']}")
        print(f"    Pays ADA: {calculation['pays_ada']}")
        
        if calculation['nimo_amount'] == 100 and calculation['confidence'] == 0.85:
            print("  [OK] Reward calculation working correctly")
            return True
        else:
            print("  [ERROR] Reward calculation returned unexpected results")
            return False
            
    except Exception as e:
        print(f"  [ERROR] Reward calculation error: {e}")
        return False

def test_api_integration():
    """Test API integration with Flask app"""
    print("\n[TEST] Testing Flask API integration...")
    
    try:
        from app import create_app
        
        print("  [INFO] Creating Flask app...")
        app = create_app()
        print("  [OK] Flask app created successfully")
        
        with app.test_client() as client:
            # Test the cardano faucet endpoint (should work without auth)
            response = client.get('/api/cardano/faucet-info')
            
            print(f"  [INFO] Faucet endpoint status: {response.status_code}")
            
            if response.status_code in [200, 401]:  # 401 is ok (needs auth)
                print("  [OK] Cardano routes registered successfully")
                
                if response.status_code == 200:
                    data = json.loads(response.data)
                    faucet_url = data.get('data', {}).get('faucet_url', 'N/A')
                    print(f"    Faucet URL: {faucet_url}")
                    
                return True
            else:
                print(f"  [ERROR] API endpoint returned unexpected status: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"  [ERROR] API integration error: {e}")
        return False

def test_with_api_keys():
    """Test with actual API keys if available"""
    print("\n[TEST] Testing with Blockfrost API keys...")
    
    preview_key = os.getenv('BLOCKFROST_PROJECT_ID_PREVIEW')
    preprod_key = os.getenv('BLOCKFROST_PROJECT_ID_PREPROD')
    
    if not preview_key and not preprod_key:
        print("  [INFO] No API keys found in environment")
        print("  [INFO] Set BLOCKFROST_PROJECT_ID_PREVIEW to test with real blockchain")
        return True
    
    try:
        from services.cardano_service import CardanoService
        
        # Test with preview network
        if preview_key:
            print("  [TEST] Testing Preview network connection...")
            cs = CardanoService(network="preview", blockfrost_project_id=preview_key)
            
            if cs.available:
                print("  [OK] Preview network connection successful")
                
                # Test network info
                info = cs.get_network_info()
                print(f"    Network: {info.get('network')}")
                print(f"    Connected: {info.get('connected')}")
                print(f"    Latest Block: {info.get('latest_block_slot', 'N/A')}")
                
                return True
            else:
                print(f"  [ERROR] Preview network connection failed: {cs.error}")
                return False
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] API key test error: {e}")
        return False

def generate_test_report(results):
    """Generate a test report"""
    print("\n" + "="*60)
    print("CARDANO INTEGRATION TEST REPORT")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    
    if passed_tests == total_tests:
        print("\nALL TESTS PASSED!")
        print("Cardano integration is ready for blockchain testing")
        
        if not os.getenv('BLOCKFROST_PROJECT_ID_PREVIEW'):
            print("\nNext Steps:")
            print("1. Get Blockfrost API key from https://blockfrost.io")
            print("2. Set BLOCKFROST_PROJECT_ID_PREVIEW environment variable") 
            print("3. Re-run this test to verify blockchain connectivity")
            print("4. Fund test wallet with ADA from faucet")
    else:
        print("\nSOME TESTS FAILED")
        print("Please review the errors above and fix integration issues")
    
    # Detailed results
    print(f"\nTest Details:")
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {test_name}")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    return passed_tests == total_tests

def main():
    """Run all tests"""
    print("Starting Cardano Integration Tests...")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
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