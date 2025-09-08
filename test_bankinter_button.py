#!/usr/bin/env python3
"""
Test script for Bankinter functionality from command line
"""

import requests
import time

def test_bankinter_endpoint():
    """Test both Bankinter endpoints"""
    
    # Backend URL
    backend_url = "http://localhost:8001"
    
    print("Testing Bankinter endpoints...")
    
    # First login
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
    
    # Test simple endpoint first
    print("2. Testing simple endpoint...")
    try:
        response = requests.post(
            f'{backend_url}/bankinter/update-movements',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("Simple endpoint works!")
            print(f"Response: {response.json()}")
        else:
            print(f"Simple endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"Simple endpoint error: {e}")
    
    # Test real endpoint with shorter timeout
    print("3. Testing real endpoint (short timeout)...")
    try:
        response = requests.post(
            f'{backend_url}/bankinter-real/update-movements-real',
            headers=headers,
            timeout=5  # Very short timeout for testing
        )
        
        if response.status_code == 200:
            print("Real endpoint works!")
            print(f"Response: {response.json()}")
        else:
            print(f"Real endpoint failed: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("Real endpoint timeout (expected - scraper takes time)")
    except Exception as e:
        print(f"Real endpoint error: {e}")

if __name__ == "__main__":
    test_bankinter_endpoint()