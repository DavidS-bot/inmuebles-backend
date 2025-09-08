#!/usr/bin/env python3
"""Test the date range deletion functionality"""

import requests
import json

def test_date_range_delete():
    """Test the date range deletion endpoint"""
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
    
    print("=== Testing Date Range Delete Functionality ===")
    
    # First, get current movements count
    movements_response = requests.get(f"{base_url}/financial-movements/", headers=headers)
    if movements_response.status_code == 200:
        movements_before = movements_response.json()
        print(f"Current movements count: {len(movements_before)}")
        
        if len(movements_before) == 0:
            print("No movements found. Creating some test movements first...")
            # Create test movements if none exist
            test_movement = {
                "property_id": 1,
                "date": "2024-01-15",
                "concept": "Test movement for deletion",
                "amount": 100.0,
                "category": "Gasto"
            }
            create_response = requests.post(f"{base_url}/financial-movements/", json=test_movement, headers=headers)
            if create_response.status_code != 200:
                print(f"Failed to create test movement: {create_response.status_code}")
                return
            print("Test movement created")
    else:
        print(f"Failed to get movements: {movements_response.status_code}")
        return
    
    # Test the date range deletion endpoint
    print("\n--- Testing Date Range Deletion ---")
    
    # Test with a specific date range
    test_params = {
        "start_date": "2024-01-01",
        "end_date": "2024-01-31"
    }
    
    delete_url = f"{base_url}/financial-movements/bulk-delete-by-date"
    query_string = "&".join([f"{k}={v}" for k, v in test_params.items()])
    full_url = f"{delete_url}?{query_string}"
    
    print(f"DELETE request URL: {full_url}")
    
    delete_response = requests.delete(full_url, headers=headers)
    
    print(f"Response status: {delete_response.status_code}")
    print(f"Response headers: {dict(delete_response.headers)}")
    print(f"Response body: {delete_response.text}")
    
    if delete_response.status_code == 200:
        result = delete_response.json()
        print(f"[SUCCESS] Date range deletion worked!")
        print(f"  Deleted count: {result.get('deleted_count', 'N/A')}")
        print(f"  Date range: {result.get('start_date')} to {result.get('end_date')}")
        print(f"  Message: {result.get('message')}")
        
        # Verify by getting movements again
        after_response = requests.get(f"{base_url}/financial-movements/", headers=headers)
        if after_response.status_code == 200:
            movements_after = after_response.json()
            print(f"  Movements after deletion: {len(movements_after)}")
        
    else:
        print(f"[ERROR] Date range deletion failed: {delete_response.status_code}")
        print(f"Error details: {delete_response.text}")
    
    print("\n--- Testing with Property Filter ---")
    
    # Test with property filter
    test_params_with_property = {
        "start_date": "2024-01-01", 
        "end_date": "2024-12-31",
        "property_id": "1"  # Test with property 1
    }
    
    query_string = "&".join([f"{k}={v}" for k, v in test_params_with_property.items()])
    full_url = f"{delete_url}?{query_string}"
    
    print(f"DELETE request URL with property: {full_url}")
    
    delete_response2 = requests.delete(full_url, headers=headers)
    print(f"Response status: {delete_response2.status_code}")
    
    if delete_response2.status_code == 200:
        result = delete_response2.json()
        print(f"[SUCCESS] Property-specific deletion worked!")
        print(f"  Deleted count: {result.get('deleted_count', 'N/A')}")
        print(f"  Property ID: {result.get('property_id')}")
    else:
        print(f"[ERROR] Property-specific deletion failed: {delete_response2.status_code}")
        print(f"Error details: {delete_response2.text}")

if __name__ == "__main__":
    test_date_range_delete()