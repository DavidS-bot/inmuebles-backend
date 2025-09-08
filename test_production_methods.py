#!/usr/bin/env python3
"""
Test different HTTP methods on production endpoints
"""

import requests

def test_production_methods():
    """Test different HTTP methods"""
    
    # Production backend URL
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    print("Testing production endpoints with different methods...")
    
    # Login first
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
    
    # Test different endpoints and methods
    endpoints_to_test = [
        ('/bankinter/update-movements', ['GET', 'POST']),
        ('/bankinter-real/update-movements-real', ['GET', 'POST']),
        ('/integrations/bankinter/sync-now', ['GET', 'POST']),
    ]
    
    for endpoint, methods in endpoints_to_test:
        print(f"\nTesting endpoint: {endpoint}")
        
        for method in methods:
            try:
                if method == 'GET':
                    response = requests.get(f'{backend_url}{endpoint}', headers=headers, timeout=10)
                else:
                    response = requests.post(f'{backend_url}{endpoint}', headers=headers, json={}, timeout=10)
                
                print(f"  {method}: {response.status_code}")
                if response.status_code == 200:
                    print(f"    Response: {response.json()}")
                elif response.status_code not in [404, 405]:
                    print(f"    Error: {response.text[:100]}")
                    
            except Exception as e:
                print(f"  {method}: Exception - {e}")

if __name__ == "__main__":
    test_production_methods()