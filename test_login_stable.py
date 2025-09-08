#!/usr/bin/env python3
"""Test login on stable URL"""

import requests

FRONTEND_URL = "https://inmuebles-david.vercel.app"
BACKEND_URL = "https://inmuebles-backend-api.onrender.com"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

def test_backend_login():
    print("Testing backend login...")
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            data={"username": EMAIL, "password": PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        if response.status_code == 200:
            token = response.json().get("access_token", "")
            print(f"✓ Backend login successful - Token: {token[:20]}...")
            return True
        else:
            print(f"✗ Backend login failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Backend error: {e}")
        return False

def test_frontend_access():
    print("Testing frontend access...")
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        if response.status_code in [200, 401]:  # 401 is normal (redirects to login)
            print("✓ Frontend accessible")
            return True
        else:
            print(f"✗ Frontend issue: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Frontend error: {e}")
        return False

def main():
    print("LOGIN TEST - STABLE URL")
    print("=" * 30)
    print(f"Frontend: {FRONTEND_URL}")
    print(f"Backend: {BACKEND_URL}")
    print(f"Credentials: {EMAIL} / {PASSWORD}")
    print()
    
    backend_ok = test_backend_login()
    frontend_ok = test_frontend_access()
    
    print("\nRESULTS:")
    print("=" * 30)
    if backend_ok and frontend_ok:
        print("✓ READY TO USE!")
        print(f"✓ Go to: {FRONTEND_URL}")
        print(f"✓ Login with: {EMAIL} / {PASSWORD}")
    else:
        print("✗ Issues detected:")
        if not backend_ok:
            print("  - Backend login problem")
        if not frontend_ok:
            print("  - Frontend access problem")

if __name__ == "__main__":
    main()