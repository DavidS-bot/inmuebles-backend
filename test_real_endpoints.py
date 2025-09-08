#!/usr/bin/env python3
"""
Test real endpoints in production that might do actual scraping
"""

import requests
import time

def test_real_endpoints():
    """Test real endpoints that might work"""
    
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    print("Testing real Bankinter endpoints...")
    
    # Login
    login_data = {'username': 'davsanchez21277@gmail.com', 'password': '123456'}
    response = requests.post(
        f'{backend_url}/auth/login',
        data=login_data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        timeout=30
    )
    
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        return
    
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    print("Login successful")
    
    # Test endpoints that might do real scraping
    endpoints_to_test = [
        ('/integrations/bankinter/download', {
            "username": "75867185",
            "password": "Motoreta123$",
            "days_back": 90,
            "auto_categorize": True,
            "import_to_system": True
        }),
        ('/bankinter-v2/update-movements-v2', {}),
        ('/bankinter/test-connection', {}),
        ('/integrations/bankinter/test-connection', {
            "username": "75867185",
            "password": "Motoreta123$"
        })
    ]
    
    for endpoint, payload in endpoints_to_test:
        print(f"\nTesting: {endpoint}")
        
        try:
            response = requests.post(
                f'{backend_url}{endpoint}',
                headers=headers,
                json=payload,
                timeout=60  # 1 minute timeout
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("SUCCESS! Response:")
                for key, value in list(result.items())[:10]:  # Show first 10 items
                    print(f"  {key}: {value}")
                    
                # If this looks like it's doing real work, let it continue
                if any(word in str(result) for word in ['scraping', 'chrome', 'selenium', 'downloading']):
                    print("This endpoint seems to do real scraping!")
                    return endpoint, payload
            else:
                print(f"Failed: {response.status_code}")
                if response.status_code != 404:
                    print(f"Error: {response.text[:200]}")
                    
        except requests.exceptions.Timeout:
            print("TIMEOUT - This might be doing real work!")
            return endpoint, payload
        except Exception as e:
            print(f"Exception: {e}")
    
    print("\nNo real scraping endpoints found in production")

if __name__ == "__main__":
    result = test_real_endpoints()
    if result:
        endpoint, payload = result
        print(f"\nFound working endpoint: {endpoint}")
        print(f"Payload: {payload}")