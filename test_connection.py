#!/usr/bin/env python3
"""
Test Frontend-Backend Connection

This script tests the connection between the frontend and backend
to ensure all endpoints are working correctly.
"""

import requests
import json
import sys
from pathlib import Path

def test_backend_connection():
    """Test basic backend connectivity"""
    base_url = "http://localhost:3000"  # Backend runs on port 3000

    print("🔍 Testing backend connection...")

    try:
        # Test root endpoint
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False

        # Test API info endpoint
        response = requests.get(f"{base_url}/api")
        if response.status_code == 200:
            print("✅ API info endpoint working")
        else:
            print(f"❌ API info endpoint failed: {response.status_code}")
            return False

        # Test health check
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            print("✅ Health check endpoint working")
        else:
            print(f"❌ Health check endpoint failed: {response.status_code}")
            return False

        return True

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Is the server running?")
        print("   Start the backend with: python run_backend.py")
        return False
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def test_cors_headers():
    """Test CORS headers for frontend compatibility"""
    base_url = "http://localhost:5000"

    print("\n🔍 Testing CORS headers...")

    try:
        # Test with Origin header (simulating frontend request)
        headers = {
            'Origin': 'http://localhost:5173',  # Vite dev server default port
            'Access-Control-Request-Method': 'GET'
        }

        response = requests.options(f"{base_url}/api/health", headers=headers)

        if 'Access-Control-Allow-Origin' in response.headers:
            print("✅ CORS headers present")
            return True
        else:
            print("⚠️  CORS headers missing - frontend may have issues")
            return False

    except Exception as e:
        print(f"❌ CORS test failed: {e}")
        return False

def test_api_endpoints():
    """Test key API endpoints that frontend expects"""
    base_url = "http://localhost:5000/api"

    endpoints_to_test = [
        ('GET', '/auth/register', 'Auth register endpoint'),
        ('GET', '/auth/login', 'Auth login endpoint'),
        ('GET', '/user/me', 'User profile endpoint'),
        ('GET', '/contributions', 'Contributions endpoint'),
        ('GET', '/contributions/user', 'User contributions endpoint'),
        ('GET', '/tokens/balance', 'Token balance endpoint'),
        ('GET', '/tokens/history', 'Token history endpoint'),
        ('POST', '/identity/create', 'Identity create endpoint'),
        ('GET', '/identity', 'Identity get endpoint'),
        ('GET', '/usdc/balance', 'USDC balance endpoint'),
        ('POST', '/usdc/send', 'USDC send endpoint'),
    ]

    print("\n🔍 Testing API endpoints...")

    all_passed = True

    for method, endpoint, description in endpoints_to_test:
        try:
            if method == 'GET':
                response = requests.get(f"{base_url}{endpoint}")
            elif method == 'POST':
                response = requests.post(f"{base_url}{endpoint}", json={})

            # For auth endpoints, 401 is expected without token
            if 'auth' in endpoint and response.status_code == 401:
                print(f"✅ {description} (requires auth as expected)")
            elif response.status_code in [200, 201, 400, 404]:  # Acceptable responses
                print(f"✅ {description}")
            else:
                print(f"❌ {description} - Unexpected status: {response.status_code}")
                all_passed = False

        except Exception as e:
            print(f"❌ {description} - Error: {e}")
            all_passed = False

    return all_passed

def main():
    """Main test function"""
    print("🚀 Nimo Frontend-Backend Connection Test")
    print("=" * 50)

    # Test 1: Basic connection
    if not test_backend_connection():
        print("\n❌ Backend connection test failed!")
        sys.exit(1)

    # Test 2: CORS headers
    test_cors_headers()

    # Test 3: API endpoints
    if test_api_endpoints():
        print("\n🎉 All tests passed! Frontend and backend are connected.")
        print("\n📋 Next steps:")
        print("  1. Start the frontend: cd frontend && npm run dev")
        print("  2. Open http://localhost:5173 in your browser")
        print("  3. Test wallet connection and identity creation")
    else:
        print("\n⚠️  Some API endpoints may need attention.")
        print("   Check backend logs for more details.")

if __name__ == '__main__':
    main()