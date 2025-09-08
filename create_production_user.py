#!/usr/bin/env python3
"""Create user in production database"""

import requests
import json

API = "https://inmuebles-backend-api.onrender.com"

def create_user():
    print("Creating user in production...")
    
    # Test if user already exists by trying to login
    login_data = {"username": "davsanchez21277@gmail.com", "password": "123456"}
    response = requests.post(f"{API}/auth/login", data=login_data, timeout=10)
    
    if response.status_code == 200:
        print("User already exists and login works!")
        return True
    
    # Try to register new user
    user_data = {
        "email": "davsanchez21277@gmail.com",
        "password": "123456",
        "full_name": "David Sanchez"
    }
    
    try:
        response = requests.post(f"{API}/auth/register", json=user_data, timeout=10)
        if response.status_code in [200, 201]:
            print("User created successfully!")
            return True
        else:
            print(f"Register failed: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"Error creating user: {e}")
        return False

def test_login():
    print("\nTesting login...")
    login_data = {"username": "davsanchez21277@gmail.com", "password": "123456"}
    
    try:
        response = requests.post(
            f"{API}/auth/login", 
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        print(f"Login response: {response.status_code}")
        if response.status_code == 200:
            print("Login successful!")
            token = response.json().get("access_token", "")[:20] + "..."
            print(f"Token received: {token}")
        else:
            print(f"Login failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"Login error: {e}")

def check_backend_health():
    print("Checking backend health...")
    try:
        response = requests.get(f"{API}/health", timeout=5)
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print("Backend is healthy!")
    except Exception as e:
        print(f"Health check failed: {e}")

def main():
    print("Production User Setup")
    print("=" * 40)
    
    # Check backend
    check_backend_health()
    
    # Create user if needed
    create_user()
    
    # Test login
    test_login()
    
    print("\nSetup completed!")
    print("Try logging in with:")
    print("  Email: davsanchez21277@gmail.com")
    print("  Password: 123456")

if __name__ == "__main__":
    main()