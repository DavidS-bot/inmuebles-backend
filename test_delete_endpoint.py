#!/usr/bin/env python3
"""
Test the delete property endpoint
"""

import requests

def test_delete_endpoint():
    backend_url = "http://localhost:8000"
    
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
    
    # Get properties to test with
    response = requests.get(
        f'{backend_url}/properties',
        headers=headers,
        timeout=30
    )
    
    if response.status_code != 200:
        print(f"Failed to get properties: {response.status_code}")
        return
    
    properties = response.json()
    if not properties:
        print("No properties found - creating a test property first")
        
        # Create a test property
        test_property = {
            "address": "Test Property for Delete Test",
            "property_type": "Piso",
            "rooms": 2,
            "m2": 80,
            "purchase_price": 100000
        }
        
        create_response = requests.post(
            f'{backend_url}/properties',
            json=test_property,
            headers=headers,
            timeout=30
        )
        
        if create_response.status_code != 200:
            print(f"Failed to create test property: {create_response.status_code}")
            print(f"Response: {create_response.text}")
            return
        
        property_data = create_response.json()
        property_id = property_data['id']
        print(f"Created test property with ID: {property_id}")
        
    else:
        # Use the first property
        test_property = properties[0]
        property_id = test_property['id']
        print(f"Using existing property ID: {property_id}")
        print(f"Property: {test_property.get('address', 'N/A')}")
    
    # Test OPTIONS request first
    print(f"\nTesting OPTIONS request for property {property_id}")
    options_response = requests.options(
        f'{backend_url}/properties/{property_id}',
        headers=headers,
        timeout=30
    )
    
    print(f"OPTIONS request status: {options_response.status_code}")
    print(f"Allowed methods: {options_response.headers.get('Allow', 'Not specified')}")
    
    # Test actual DELETE request
    print(f"\nTesting DELETE request for property {property_id}")
    
    confirmation = input("Do you want to actually delete this property? (y/N): ")
    if confirmation.lower() == 'y':
        delete_response = requests.delete(
            f'{backend_url}/properties/{property_id}',
            headers=headers,
            timeout=30
        )
        
        print(f"DELETE request status: {delete_response.status_code}")
        if delete_response.status_code == 200:
            print("✅ Property deleted successfully!")
            print(f"Response: {delete_response.json()}")
        else:
            print("❌ Delete failed")
            print(f"Response: {delete_response.text}")
    else:
        print("Skipping actual deletion")

if __name__ == "__main__":
    test_delete_endpoint()