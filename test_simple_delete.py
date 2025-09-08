#!/usr/bin/env python3
"""Simple test to verify the endpoint exists"""

import requests

def test_endpoint_exists():
    """Test if the endpoint exists and responds correctly"""
    base_url = "http://localhost:8000"
    
    # Login first
    login_data = {
        "username": "davsanchez21277@gmail.com",
        "password": "123456"
    }
    
    response = requests.post(
        f"{base_url}/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("Testing endpoint existence...")
    
    # Test with curl-like approach but with proper token
    test_url = f"{base_url}/financial-movements/bulk-delete-by-date?start_date=2024-01-01&end_date=2024-01-31"
    
    print(f"Making request to: {test_url}")
    print(f"Headers: {headers}")
    
    try:
        response = requests.delete(test_url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("SUCCESS: Endpoint is working!")
        elif response.status_code == 400:
            print("Expected error: Bad request (probably invalid parameters)")
        elif response.status_code == 422:
            print("ERROR: Still getting validation error - route conflict issue persists")
        else:
            print(f"Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_endpoint_exists()