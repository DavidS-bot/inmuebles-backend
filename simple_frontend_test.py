#!/usr/bin/env python3

import requests
import json

def test_frontend_bankinter():
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    print("Testing frontend Bankinter functionality...")
    
    # Login
    login_data = {'username': 'davsanchez21277@gmail.com', 'password': '123456'}
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
    print("Login successful")
    
    # Test Bankinter endpoint exactly like frontend
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    
    print("Testing Bankinter sync...")
    
    try:
        response = requests.post(
            f'{backend_url}/integrations/bankinter/sync-now',
            headers=headers,
            json={},
            timeout=30  # Short timeout for testing
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS!")
            print("Response:")
            for key, value in result.items():
                print(f"  {key}: {value}")
        else:
            print("FAILED!")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_frontend_bankinter()