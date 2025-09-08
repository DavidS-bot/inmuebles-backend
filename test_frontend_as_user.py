#!/usr/bin/env python3
"""Test what the frontend actually shows after login"""

import requests
import json

PROD_API = "https://inmuebles-backend-api.onrender.com"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

def test_frontend_behavior():
    print("TESTING FRONTEND BEHAVIOR (SIMULATING USER)")
    print("=" * 50)
    
    # 1. Login to get token
    response = requests.post(f"{PROD_API}/auth/login", 
                           data={"username": EMAIL, "password": PASSWORD}, timeout=10)
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login successful, got token")
    
    print("\n1. TESTING DASHBOARD DATA CALLS:")
    print("-" * 30)
    
    # Dashboard calls these endpoints
    dashboard_calls = [
        ("/properties", "Properties for dashboard"),
        ("/mortgage-details", "WITHOUT slash (frontend bug)"),
        ("/mortgage-details/", "WITH slash (correct)"),
        ("/analytics/portfolio-summary?year=2025", "Analytics backup")
    ]
    
    for endpoint, description in dashboard_calls:
        try:
            r = requests.get(f"{PROD_API}{endpoint}", headers=headers, timeout=10)
            print(f"{description}:")
            print(f"  Status: {r.status_code}")
            
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, list):
                    print(f"  Count: {len(data)} items")
                    if "mortgage" in endpoint.lower():
                        debt = sum(item.get('outstanding_balance', 0) for item in data)
                        print(f"  Total debt: {debt:,.2f} EUR")
                else:
                    print(f"  Data type: {type(data).__name__}")
            elif r.status_code == 405:
                print(f"  ERROR: Method Not Allowed (frontend will show 0)")
        except Exception as e:
            print(f"  EXCEPTION: {str(e)[:30]}")
    
    print("\n2. TESTING CLASSIFICATION RULES PAGE:")
    print("-" * 30)
    
    # Classification rules page calls
    rules_calls = [
        ("/classification-rules", "WITHOUT slash (frontend bug)"),
        ("/classification-rules/", "WITH slash (correct)")
    ]
    
    for endpoint, description in rules_calls:
        try:
            r = requests.get(f"{PROD_API}{endpoint}", headers=headers, timeout=10)
            print(f"{description}:")
            print(f"  Status: {r.status_code}")
            
            if r.status_code == 200:
                data = r.json()
                print(f"  Count: {len(data)} rules")
            elif r.status_code == 405:
                print(f"  ERROR: Method Not Allowed (frontend will show 0)")
        except Exception as e:
            print(f"  EXCEPTION: {str(e)[:30]}")
    
    print("\n3. TESTING RENTAL CONTRACTS PAGE:")
    print("-" * 30)
    
    # Rental contracts page calls
    contracts_calls = [
        ("/rental-contracts", "WITHOUT slash (frontend bug)"),
        ("/rental-contracts/", "WITH slash (correct)")
    ]
    
    for endpoint, description in contracts_calls:
        try:
            r = requests.get(f"{PROD_API}{endpoint}", headers=headers, timeout=10)
            print(f"{description}:")
            print(f"  Status: {r.status_code}")
            
            if r.status_code == 200:
                data = r.json()
                print(f"  Count: {len(data)} contracts")
            elif r.status_code == 405:
                print(f"  ERROR: Method Not Allowed (frontend will show 0)")
        except Exception as e:
            print(f"  EXCEPTION: {str(e)[:30]}")
    
    print("\n4. DIAGNOSIS:")
    print("-" * 30)
    print("If frontend is calling endpoints WITHOUT trailing slash:")
    print("  - Dashboard will show 0.00 EUR debt (should be 336,567)")
    print("  - Classification rules will show 0 (should be 35)")
    print("  - Rental contracts will show 0 (should be 4)")
    print("\nThe frontend code needs to be updated to use trailing slashes.")

if __name__ == "__main__":
    test_frontend_behavior()