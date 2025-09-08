#!/usr/bin/env python3
"""Test mortgage endpoint formats"""

import requests

PROD_API = "https://inmuebles-backend-api.onrender.com"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

def login():
    response = requests.post(f"{PROD_API}/auth/login", 
                           data={"username": EMAIL, "password": PASSWORD}, timeout=10)
    return response.json()["access_token"] if response.status_code == 200 else None

def test_endpoints():
    token = login()
    if not token:
        print("Login failed")
        return
        
    headers = {"Authorization": f"Bearer {token}"}
    
    print("Testing mortgage endpoints:")
    
    # Test without trailing slash
    try:
        response = requests.get(f"{PROD_API}/mortgage-details", headers=headers, timeout=10)
        print(f"GET /mortgage-details: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Data: {len(data)} items")
            if data:
                total = sum(item.get('outstanding_balance', 0) for item in data)
                print(f"  Total debt: {total:,.2f} EUR")
    except Exception as e:
        print(f"GET /mortgage-details: ERROR - {e}")
    
    # Test with trailing slash
    try:
        response = requests.get(f"{PROD_API}/mortgage-details/", headers=headers, timeout=10)
        print(f"GET /mortgage-details/: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Data: {len(data)} items")
            if data:
                total = sum(item.get('outstanding_balance', 0) for item in data)
                print(f"  Total debt: {total:,.2f} EUR")
    except Exception as e:
        print(f"GET /mortgage-details/: ERROR - {e}")

if __name__ == "__main__":
    test_endpoints()