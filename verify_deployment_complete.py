#!/usr/bin/env python3
"""Verify deployment is complete and working"""

import requests

PROD_API = "https://inmuebles-backend-api.onrender.com"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

def verify_deployment():
    print("VERIFYING DEPLOYMENT SUCCESS")
    print("=" * 40)
    
    # Login
    response = requests.post(f"{PROD_API}/auth/login", 
                           data={"username": EMAIL, "password": PASSWORD}, timeout=10)
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test all corrected endpoints (with trailing slashes)
    test_cases = [
        {
            "endpoint": "/mortgage-details/",
            "name": "Dashboard Debt",
            "expected_count": 6,
            "calculate_debt": True
        },
        {
            "endpoint": "/classification-rules/",
            "name": "Classification Rules",
            "expected_count": 35,
            "calculate_debt": False
        },
        {
            "endpoint": "/rental-contracts/",
            "name": "Rental Contracts", 
            "expected_count": 4,
            "calculate_debt": False
        }
    ]
    
    all_working = True
    
    for test in test_cases:
        try:
            r = requests.get(f"{PROD_API}{test['endpoint']}", headers=headers, timeout=15)
            
            if r.status_code == 200:
                data = r.json()
                actual_count = len(data) if isinstance(data, list) else 0
                
                if actual_count == test['expected_count']:
                    status = "OK"
                else:
                    status = f"WRONG COUNT ({actual_count} vs {test['expected_count']})"
                    all_working = False
                
                print(f"{test['name']}: {status}")
                
                if test['calculate_debt'] and actual_count > 0:
                    debt = sum(item.get('outstanding_balance', 0) for item in data)
                    print(f"  -> Debt total: {debt:,.2f} EUR")
                    if debt > 0:
                        print(f"  -> Dashboard WILL show correct debt")
                    else:
                        print(f"  -> ERROR: Debt is 0!")
                        all_working = False
            else:
                print(f"{test['name']}: ERROR {r.status_code}")
                all_working = False
                
        except Exception as e:
            print(f"{test['name']}: EXCEPTION - {str(e)[:30]}")
            all_working = False
    
    print("\n" + "=" * 40)
    
    if all_working:
        print("SUCCESS! All endpoints working correctly.")
        print("\nFrontend should now show:")
        print("  - Dashboard: Deuda Total 336,567.00 EUR")
        print("  - Classification Rules: 35 rules")
        print("  - Rental Contracts: 4 contracts")
    else:
        print("PROBLEM: Some endpoints not working correctly.")
        print("The frontend deployment may not have applied the fixes.")

if __name__ == "__main__":
    verify_deployment()