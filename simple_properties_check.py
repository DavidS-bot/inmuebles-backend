#!/usr/bin/env python3
"""
Simple properties check
"""

import requests

PRODUCTION_URL = "https://inmuebles-backend-api.onrender.com"

def main():
    # Login first
    login_response = requests.post(
        f"{PRODUCTION_URL}/auth/login",
        data={
            'username': 'davsanchez21277@gmail.com',
            'password': '123456'
        }
    )
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code}")
        return
    
    token = login_response.json().get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
    
    # Try different property endpoints
    endpoints = [
        "/properties",
        "/properties/",
        "/property",
        "/property/"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"Testing: {endpoint}")
            response = requests.get(f"{PRODUCTION_URL}{endpoint}", headers=headers)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    first_property = data[0]
                    print(f"  Found {len(data)} properties")
                    print(f"  First property ID: {first_property.get('id')}")
                    print(f"  First property photo: {first_property.get('photo')}")
                    break
                else:
                    print(f"  Response: {data}")
            else:
                print(f"  Error: {response.text[:100]}...")
        except Exception as e:
            print(f"  Exception: {e}")
        print()

if __name__ == "__main__":
    main()