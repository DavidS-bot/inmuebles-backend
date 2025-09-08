#!/usr/bin/env python3
"""Test the exact endpoint the dashboard uses"""

import requests
import json

PROD_API = "https://inmuebles-backend-api.onrender.com"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

def test_dashboard_endpoints():
    print("TESTING EXACT DASHBOARD ENDPOINTS")
    print("=" * 40)
    
    # Login
    try:
        response = requests.post(f"{PROD_API}/auth/login", 
                               data={"username": EMAIL, "password": PASSWORD}, timeout=10)
        if response.status_code != 200:
            print(f"Login failed: {response.status_code}")
            return
        token = response.json()["access_token"]
        print("✓ Login successful")
    except Exception as e:
        print(f"Login error: {e}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test the exact endpoints the dashboard calls
    endpoints_to_test = [
        "/properties",
        "/mortgage-details",  # WITHOUT trailing slash (as dashboard calls it)
        "/mortgage-details/", # WITH trailing slash (as we fixed it)
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\nTesting: {endpoint}")
        try:
            response = requests.get(f"{PROD_API}{endpoint}", headers=headers, timeout=15)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  Items: {len(data) if isinstance(data, list) else 'N/A'}")
                
                if 'mortgage' in endpoint and isinstance(data, list):
                    total_debt = sum(item.get('outstanding_balance', 0) for item in data)
                    print(f"  Total debt: {total_debt:,.2f} EUR")
                    
            elif response.status_code == 405:
                print(f"  ERROR: Method Not Allowed")
            else:
                print(f"  Error response: {response.text[:100]}")
                
        except Exception as e:
            print(f"  Exception: {str(e)[:50]}")
    
    # Test current year analytics (backup endpoint for dashboard)
    current_year = 2025
    analytics_endpoint = f"/analytics/portfolio-summary?year={current_year}"
    print(f"\nTesting analytics backup: {analytics_endpoint}")
    try:
        response = requests.get(f"{PROD_API}{analytics_endpoint}", headers=headers, timeout=15)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Analytics data keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
        else:
            print(f"  Error: {response.text[:100]}")
    except Exception as e:
        print(f"  Exception: {str(e)[:50]}")

if __name__ == "__main__":
    test_dashboard_endpoints()