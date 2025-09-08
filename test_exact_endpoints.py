#!/usr/bin/env python3
"""Test exact endpoints from OpenAPI spec"""

import requests

def test_exact():
    # Login
    response = requests.post("https://inmuebles-backend-api.onrender.com/auth/login", 
                           data={"username": "davsanchez21277@gmail.com", "password": "123456"})
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test exact endpoints from OpenAPI spec
    endpoints = [
        "/classification-rules/",  # With trailing slash as in spec
        "/rental-contracts/",      # With trailing slash as in spec
    ]
    
    for endpoint in endpoints:
        print(f"Testing GET {endpoint}:")
        try:
            r = requests.get(f"https://inmuebles-backend-api.onrender.com{endpoint}", 
                           headers=headers, timeout=20)
            print(f"  Status: {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                print(f"  Items: {len(data) if isinstance(data, list) else 'N/A'}")
            elif r.status_code != 200:
                print(f"  Response: {r.text[:100]}")
        except Exception as e:
            print(f"  Error: {str(e)[:50]}")
    
    # Try POST to classification-rules with simple data
    print(f"\nTesting POST to /classification-rules/:")
    try:
        test_data = {
            "property_id": 1,
            "keyword": "test sync",
            "category": "Renta"
        }
        headers_post = {**headers, "Content-Type": "application/json"}
        r = requests.post(f"https://inmuebles-backend-api.onrender.com/classification-rules/", 
                         json=test_data, headers=headers_post, timeout=20)
        print(f"  Status: {r.status_code}")
        if r.status_code not in [200, 201]:
            print(f"  Response: {r.text[:100]}")
    except Exception as e:
        print(f"  Error: {str(e)[:50]}")

if __name__ == "__main__":
    test_exact()