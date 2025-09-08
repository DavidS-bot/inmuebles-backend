#!/usr/bin/env python3
"""
Test Bankinter functionality in production backend
"""

import requests
import time

def test_production_bankinter():
    """Test Bankinter endpoints in production"""
    
    # Production backend URL
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    print("Testing production Bankinter endpoints...")
    
    # First check if backend is alive
    print("1. Checking backend health...")
    try:
        response = requests.get(f'{backend_url}/health', timeout=10)
        if response.status_code == 200:
            print(f"Backend healthy: {response.json()}")
        else:
            print(f"Backend health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"Backend not reachable: {e}")
        return
    
    # Try to login
    print("2. Attempting login...")
    login_data = {'username': 'davsanchez21277@gmail.com', 'password': '123456'}
    try:
        response = requests.post(
            f'{backend_url}/auth/login',
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"Login failed: {response.status_code} - {response.text}")
            return
        
        token = response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        print("Login successful")
        
    except Exception as e:
        print(f"Login error: {e}")
        return
    
    # Test different Bankinter endpoints that might exist
    endpoints_to_test = [
        '/bankinter/update-movements',
        '/bankinter-real/update-movements-real',
        '/bankinter-v2/update-movements-v2',
        '/bank-integration/sync-now'
    ]
    
    for endpoint in endpoints_to_test:
        print(f"3. Testing endpoint: {endpoint}")
        try:
            response = requests.post(
                f'{backend_url}{endpoint}',
                headers=headers,
                json={},
                timeout=10  # Short timeout for testing
            )
            
            if response.status_code == 200:
                print(f"SUCCESS: {endpoint} works!")
                print(f"Response: {response.json()}")
            elif response.status_code == 404:
                print(f"NOT FOUND: {endpoint} doesn't exist")
            else:
                print(f"ERROR: {endpoint} returned {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print(f"TIMEOUT: {endpoint} timed out (maybe it's working but slow)")
        except Exception as e:
            print(f"EXCEPTION: {endpoint} error: {e}")

if __name__ == "__main__":
    test_production_bankinter()