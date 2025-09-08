#!/usr/bin/env python3
"""Test API endpoints directly"""

import requests

PROD_API = "https://inmuebles-backend-api.onrender.com"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

def test_basic_endpoints():
    print("TESTING PRODUCTION API DIRECTLY")
    print("=" * 40)
    
    # Test health endpoint first
    try:
        response = requests.get(f"{PROD_API}/health", timeout=10)
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"  Response: {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return
    
    # Test login
    try:
        response = requests.post(f"{PROD_API}/auth/login", 
                               data={"username": EMAIL, "password": PASSWORD}, timeout=10)
        print(f"Login: {response.status_code}")
        if response.status_code != 200:
            print(f"  Login failed: {response.text[:100]}")
            return
        token = response.json()["access_token"]
        print("  Login successful!")
    except Exception as e:
        print(f"Login failed: {e}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test all endpoints
    test_endpoints = [
        "/properties",
        "/mortgage-details/",
        "/classification-rules",
        "/rental-contracts",
        "/financial-movements"
    ]
    
    for endpoint in test_endpoints:
        try:
            response = requests.get(f"{PROD_API}{endpoint}", headers=headers, timeout=15)
            print(f"GET {endpoint}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  Items: {len(data) if isinstance(data, list) else 'N/A'}")
            elif response.status_code in [405, 404]:
                print(f"  Error: {response.json().get('detail', 'Unknown error')}")
            else:
                print(f"  Response: {response.text[:50]}")
        except Exception as e:
            print(f"GET {endpoint}: ERROR - {str(e)[:50]}")
    
    # Test POST to classification-rules specifically
    print(f"\nTesting POST to classification-rules...")
    try:
        test_data = {
            "property_id": 1,
            "keyword": "test",
            "category": "Renta",
            "subcategory": "Test"
        }
        headers_post = {**headers, "Content-Type": "application/json"}
        response = requests.post(f"{PROD_API}/classification-rules", 
                               json=test_data, headers=headers_post, timeout=15)
        print(f"POST /classification-rules: {response.status_code}")
        if response.status_code not in [200, 201]:
            print(f"  Response: {response.text[:100]}")
    except Exception as e:
        print(f"POST /classification-rules: ERROR - {str(e)[:50]}")

if __name__ == "__main__":
    test_basic_endpoints()