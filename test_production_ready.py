#!/usr/bin/env python3
"""
Test script to verify the production deployment is working
"""

import requests
import time
import json

def test_production_endpoint():
    """Test the production Bankinter endpoint"""
    
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    print("🔐 Logging in to production...")
    
    # Login
    login_data = {"username": "davsanchez21277@gmail.com", "password": "123456"}
    response = requests.post(
        f"{backend_url}/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30
    )
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        return False
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Login successful")
    print("🏦 Testing Bankinter sync endpoint...")
    
    # Test Bankinter sync
    response = requests.post(
        f"{backend_url}/integrations/bankinter/sync-now",
        headers=headers,
        timeout=300  # 5 minute timeout
    )
    
    print(f"📊 Response status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Endpoint response received")
        print(f"🔍 Sync status: {result.get('sync_status', 'unknown')}")
        print(f"📝 Message: {result.get('message', 'No message')}")
        print(f"📊 Details: {result.get('details', 'No details')}")
        
        # Check if it's using the new hybrid solution
        if "Método usado:" in result.get('details', ''):
            print("🎉 NEW HYBRID SOLUTION IS WORKING!")
            print(f"🔧 Data source: {result.get('data_source', 'unknown')}")
            print(f"📈 Movements: {result.get('movements_extracted', 0)}")
            return True
        elif result.get('sync_status') == 'completed':
            print("⚠️ Old endpoint still active, but working")
            return True
        else:
            print("❌ Endpoint not working properly")
            return False
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(f"📄 Response: {response.text}")
        return False

if __name__ == "__main__":
    print("🧪 TESTING PRODUCTION DEPLOYMENT")
    print("="*50)
    
    success = test_production_endpoint()
    
    if success:
        print("\n✅ PRODUCTION TEST PASSED")
    else:
        print("\n❌ PRODUCTION TEST FAILED")
    
    exit(0 if success else 1)