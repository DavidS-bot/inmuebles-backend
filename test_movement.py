#!/usr/bin/env python3
"""
Test script to isolate movement creation issue
"""
import requests
import json

def test_movement_creation():
    backend_url = "http://localhost:8001"
    
    # Login
    login_data = {"username": "davsanchez21277@gmail.com", "password": "123456"}
    response = requests.post(
        f"{backend_url}/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30
    )
    
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}, {response.text}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Get properties
    properties_response = requests.get(f"{backend_url}/properties/", headers=headers, timeout=10)
    print(f"Properties response: {properties_response.status_code}")
    print(f"Properties: {properties_response.json()}")
    
    if properties_response.status_code == 200:
        properties = properties_response.json()
        if properties:
            property_id = properties[0]["id"]
            print(f"Using property ID: {property_id}")
        else:
            print("No properties found, need to create one first")
            return
    
    # Test movement data - simple format
    movement_obj = {
        "property_id": property_id,
        "date": "2025-08-27",
        "concept": "Test Movement",
        "amount": 27.0,
        "category": "Sin clasificar"
    }
    
    print(f"Testing movement creation: {json.dumps(movement_obj, indent=2)}")
    
    # Create movement
    response = requests.post(
        f"{backend_url}/financial-movements/",
        json=movement_obj,
        headers=headers,
        timeout=10
    )
    
    print(f"Movement creation response: {response.status_code}")
    print(f"Response content: {response.text}")

if __name__ == "__main__":
    test_movement_creation()