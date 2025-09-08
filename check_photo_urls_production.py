#!/usr/bin/env python3
"""
Check photo URLs in production
"""

import requests

PRODUCTION_URL = "https://inmuebles-backend-api.onrender.com"

def login_to_production() -> str:
    """Login and get token"""
    try:
        response = requests.post(
            f"{PRODUCTION_URL}/auth/login",
            data={
                'username': 'davsanchez21277@gmail.com',
                'password': '123456'
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('access_token')
        else:
            print(f"ERROR login: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"ERROR login: {e}")
        return None

def get_properties_with_photos(token: str):
    """Get properties and their photo URLs"""
    try:
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.get(f"{PRODUCTION_URL}/properties/", headers=headers)
        
        if response.status_code == 200:
            properties = response.json()
            print(f"Found {len(properties)} properties:")
            print()
            
            photo_count = 0
            for prop in properties:
                photo_url = prop.get('photo')
                if photo_url:
                    photo_count += 1
                    print(f"Property {prop.get('id')}: {prop.get('address')[:50]}...")
                    print(f"  Photo URL: {photo_url}")
                    
                    # Test if photo is accessible
                    try:
                        photo_response = requests.head(f"{PRODUCTION_URL}{photo_url}")
                        status = photo_response.status_code
                        print(f"  Status: {status} ({'OK' if status == 200 else 'FAILED'})")
                    except Exception as e:
                        print(f"  Status: ERROR ({e})")
                    print()
                else:
                    print(f"Property {prop.get('id')}: No photo")
            
            print(f"Summary: {photo_count}/{len(properties)} properties have photos")
            return properties
            
        else:
            print(f"ERROR getting properties: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"ERROR getting properties: {e}")
        return []

def main():
    print("=== CHECK PHOTO URLS IN PRODUCTION ===")
    print()
    
    token = login_to_production()
    if not token:
        return
    
    print("Login successful!")
    print()
    
    get_properties_with_photos(token)

if __name__ == "__main__":
    main()