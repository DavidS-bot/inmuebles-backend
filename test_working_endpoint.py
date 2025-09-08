#!/usr/bin/env python3
"""
Test the working Bankinter endpoint
"""

import requests
import time

def test_working_endpoint():
    """Test the /integrations/bankinter/sync-now endpoint"""
    
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    print("Testing the working Bankinter endpoint...")
    
    # Login
    print("1. Logging in...")
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
    
    # Test the working endpoint
    print("2. Testing /integrations/bankinter/sync-now...")
    try:
        response = requests.post(
            f'{backend_url}/integrations/bankinter/sync-now',
            headers=headers,
            json={},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS! Response:")
            for key, value in result.items():
                print(f"  {key}: {value}")
                
            # If sync started, check progress
            if result.get('progress_url'):
                print(f"\n3. Checking progress...")
                time.sleep(5)  # Wait a bit
                
                progress_response = requests.get(
                    f"{backend_url}{result['progress_url']}",
                    headers=headers,
                    timeout=10
                )
                
                if progress_response.status_code == 200:
                    progress = progress_response.json()
                    print("Progress:")
                    for key, value in progress.items():
                        print(f"  {key}: {value}")
                else:
                    print(f"Progress check failed: {progress_response.status_code}")
        else:
            print(f"Failed: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_working_endpoint()