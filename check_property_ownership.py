#!/usr/bin/env python3
"""Check property ownership for the movement that's failing to delete"""

import requests

def check_ownership():
    print("Checking property ownership...")
    
    # Login
    login_data = {'username': 'davsanchez21277@gmail.com', 'password': '123456'}
    try:
        response = requests.post(
            'https://inmuebles-backend-api.onrender.com/auth/login',
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=15
        )
        
        if response.status_code != 200:
            print(f"Login failed: {response.status_code}")
            return
            
        token = response.json()['access_token']
        print("Login successful")
        
        headers = {'Authorization': f'Bearer {token}'}
        
        # Get user properties
        properties_response = requests.get(
            'https://inmuebles-backend-api.onrender.com/properties/',
            headers=headers,
            timeout=15
        )
        
        if properties_response.status_code != 200:
            print(f"Failed to get properties: {properties_response.status_code}")
            return
            
        properties = properties_response.json()
        print(f"User owns {len(properties)} properties:")
        
        property_ids = []
        for prop in properties:
            prop_id = prop.get('id')
            property_ids.append(prop_id)
            print(f"  - Property {prop_id}: {prop.get('address', 'No address')}")
        
        print(f"\nProperty IDs owned by user: {property_ids}")
        
        # Check if property 10 is in the list
        if 10 in property_ids:
            print("✅ User OWNS property 10 - deletion should work")
        else:
            print("❌ User does NOT own property 10 - this is why deletion fails!")
            print("The movement belongs to a property the user doesn't own.")
        
        # Also check if there are any truly unassigned movements
        movements_response = requests.get(
            'https://inmuebles-backend-api.onrender.com/financial-movements/?limit=200',
            headers=headers,
            timeout=15
        )
        
        if movements_response.status_code == 200:
            movements = movements_response.json()
            unassigned = [m for m in movements if m.get('property_id') is None]
            print(f"\nFound {len(unassigned)} truly unassigned movements")
            if unassigned:
                print(f"Example unassigned movement: {unassigned[0].get('concept', '')[:50]}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    check_ownership()