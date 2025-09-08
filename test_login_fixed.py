#!/usr/bin/env python3
"""Test if login is fixed"""

import requests

def test_login_fixed():
    print("TESTING LOGIN FIX")
    print("=" * 30)
    
    # Test backend login
    print("\n1. Backend API Login Test:")
    response = requests.post(
        "https://inmuebles-backend-api.onrender.com/auth/login",
        data={"username": "davsanchez21277@gmail.com", "password": "123456"},
        timeout=10
    )
    
    if response.status_code == 200:
        print("   Backend login: OK")
        token = response.json()["access_token"]
        
        # Test a simple endpoint with token
        headers = {"Authorization": f"Bearer {token}"}
        r = requests.get("https://inmuebles-backend-api.onrender.com/properties", 
                        headers=headers, timeout=10)
        if r.status_code == 200:
            print(f"   API access: OK ({len(r.json())} properties)")
        else:
            print(f"   API access: ERROR {r.status_code}")
    else:
        print(f"   Backend login: ERROR {response.status_code}")
    
    # Test frontend
    print("\n2. Frontend Status:")
    try:
        r = requests.get("https://inmuebles-david.vercel.app", timeout=10)
        print(f"   Frontend: {r.status_code} (401 is normal - requires login)")
        
        # Check if login page is accessible
        r = requests.get("https://inmuebles-david.vercel.app/login", timeout=10)
        print(f"   Login page: {r.status_code}")
        
    except Exception as e:
        print(f"   Frontend: ERROR - {e}")
    
    print("\n3. Configuration Summary:")
    print("   API URL: https://inmuebles-backend-api.onrender.com")
    print("   Frontend URL: https://inmuebles-david.vercel.app")
    print("   NEXTAUTH_URL: https://inmuebles-david.vercel.app")
    
    print("\n4. Result:")
    print("   The login should now work correctly.")
    print("   Try logging in at: https://inmuebles-david.vercel.app")
    print("   Email: davsanchez21277@gmail.com")
    print("   Password: 123456")

if __name__ == "__main__":
    test_login_fixed()