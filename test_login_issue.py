#!/usr/bin/env python3
"""Test login issue"""

import requests
import json

PROD_API = "https://inmuebles-backend-api.onrender.com"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

def test_login():
    print("TESTING LOGIN ISSUE")
    print("=" * 30)
    
    # Test 1: Backend API login
    print("\n1. Testing Backend API Login:")
    try:
        response = requests.post(
            f"{PROD_API}/auth/login",
            data={"username": EMAIL, "password": PASSWORD},
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                print(f"   SUCCESS: Got token")
                print(f"   Token starts with: {data['access_token'][:20]}...")
            else:
                print(f"   ERROR: No token in response")
                print(f"   Response: {data}")
        else:
            print(f"   ERROR: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"   EXCEPTION: {e}")
    
    # Test 2: Check CORS headers
    print("\n2. Testing CORS Configuration:")
    try:
        response = requests.options(
            f"{PROD_API}/auth/login",
            headers={"Origin": "https://inmuebles-david.vercel.app"},
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        print(f"   CORS Headers:")
        for header, value in response.headers.items():
            if 'access-control' in header.lower():
                print(f"     {header}: {value}")
                
    except Exception as e:
        print(f"   EXCEPTION: {e}")
    
    # Test 3: Check frontend URL
    print("\n3. Testing Frontend Connectivity:")
    try:
        response = requests.get("https://inmuebles-david.vercel.app", timeout=10)
        print(f"   Frontend status: {response.status_code}")
        
    except Exception as e:
        print(f"   EXCEPTION: {e}")
    
    # Test 4: Check environment variable configuration
    print("\n4. Checking Environment Configuration:")
    print(f"   Backend API URL: {PROD_API}")
    print(f"   Frontend URL: https://inmuebles-david.vercel.app")
    print(f"   Expected env var: NEXT_PUBLIC_API_URL={PROD_API}")
    
    print("\n5. Common Login Issues:")
    print("   - Wrong API URL in frontend .env")
    print("   - CORS blocking requests")
    print("   - Token not being stored properly")
    print("   - Cookie/localStorage issues")

if __name__ == "__main__":
    test_login()