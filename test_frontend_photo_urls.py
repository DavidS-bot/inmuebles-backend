#!/usr/bin/env python3
"""
Test how frontend would handle the photo URLs
"""

import requests

def test_photo_urls():
    # Get properties from production
    login_response = requests.post(
        "https://inmuebles-backend-api.onrender.com/auth/login",
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
    
    # Get properties
    response = requests.get("https://inmuebles-backend-api.onrender.com/properties", headers=headers)
    
    if response.status_code != 200:
        print(f"Properties request failed: {response.status_code}")
        return
    
    properties = response.json()
    
    print(f"Testing photo URLs for {len(properties)} properties:")
    print()
    
    for prop in properties:
        photo_url = prop.get('photo')
        if photo_url:
            print(f"Property {prop.get('id')}: {prop.get('address')[:40]}...")
            print(f"  Photo URL: {photo_url}")
            print(f"  Starts with http: {photo_url.startswith('http')}")
            
            # Test if URL is accessible
            try:
                # For relative paths, prepend the production URL
                full_url = photo_url if photo_url.startswith('http') else f"https://inmuebles-backend-api.onrender.com{photo_url}"
                print(f"  Full URL: {full_url}")
                
                photo_response = requests.head(full_url)
                print(f"  Status: {photo_response.status_code}")
                if photo_response.status_code == 200:
                    content_type = photo_response.headers.get('content-type', 'unknown')
                    print(f"  Content-Type: {content_type}")
                    print(f"  OK - URL is working correctly")
                else:
                    print(f"  FAILED - URL failed")
            except Exception as e:
                print(f"  ERROR - {e}")
            
            print()

if __name__ == "__main__":
    test_photo_urls()