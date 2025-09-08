#!/usr/bin/env python3
"""Fresh diagnosis of the entire system"""

import requests

PROD_API = "https://inmuebles-backend-api.onrender.com"
FRONTEND_URL = "https://inmuebles-david.vercel.app"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

def fresh_diagnosis():
    print("COMPLETE SYSTEM DIAGNOSIS")
    print("=" * 40)
    
    # 1. Test production API
    print("\n1. PRODUCTION API STATUS:")
    try:
        response = requests.post(f"{PROD_API}/auth/login", 
                               data={"username": EMAIL, "password": PASSWORD}, timeout=10)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("  - Login: OK")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test key endpoints
            endpoints = [
                "/properties",
                "/mortgage-details/",
                "/classification-rules/", 
                "/rental-contracts/"
            ]
            
            for endpoint in endpoints:
                try:
                    r = requests.get(f"{PROD_API}{endpoint}", headers=headers, timeout=10)
                    if r.status_code == 200:
                        data = r.json()
                        count = len(data) if isinstance(data, list) else 0
                        print(f"  - {endpoint}: {count} items")
                        
                        if endpoint == "/mortgage-details/":
                            debt = sum(item.get('outstanding_balance', 0) for item in data)
                            print(f"    Total debt: {debt:,.2f} EUR")
                    else:
                        print(f"  - {endpoint}: ERROR {r.status_code}")
                except:
                    print(f"  - {endpoint}: TIMEOUT/ERROR")
        else:
            print("  - Login: FAILED")
    except:
        print("  - API: UNREACHABLE")
    
    # 2. Test frontend
    print(f"\n2. FRONTEND STATUS:")
    try:
        response = requests.get(f"{FRONTEND_URL}", timeout=10)
        print(f"  - Frontend: {response.status_code} (requires login)")
    except:
        print("  - Frontend: UNREACHABLE")
    
    # 3. Check local backend
    print(f"\n3. LOCAL BACKEND STATUS:")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("  - Local backend: RUNNING")
        else:
            print("  - Local backend: ERROR")
    except:
        print("  - Local backend: NOT RUNNING")
    
    print(f"\n4. WHAT DO YOU NEED HELP WITH?")
    print(f"Please tell me specifically what issues you're seeing:")
    print(f"  - Dashboard showing wrong values?")
    print(f"  - Classification rules not working?") 
    print(f"  - Rental contracts missing?")
    print(f"  - API endpoints not responding?")
    print(f"  - Something else?")

if __name__ == "__main__":
    fresh_diagnosis()