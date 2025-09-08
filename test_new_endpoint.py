#!/usr/bin/env python3
"""Test the new endpoint name"""

import requests

def test_new_endpoint():
    """Test the new endpoint name"""
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
    
    print("Testing new endpoint name...")
    
    test_url = f"{base_url}/financial-movements/delete-by-date-range?start_date=2024-01-01&end_date=2024-01-31"
    
    print(f"Making request to: {test_url}")
    
    try:
        response = requests.delete(test_url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("[SUCCESS] Endpoint is working!")
            print(f"  Deleted count: {result.get('deleted_count', 'N/A')}")
            print(f"  Date range: {result.get('start_date')} to {result.get('end_date')}")
        else:
            print(f"Endpoint responded with status: {response.status_code}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_new_endpoint()