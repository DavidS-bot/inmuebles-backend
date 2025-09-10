#!/usr/bin/env python3

import requests
import json

def check_user_properties():
    """Check if main user has properties"""
    
    print("CHECKING USER PROPERTIES")
    print("=" * 50)
    
    # Login
    login_data = {
        "username": "davsanchez21277@gmail.com",
        "password": "123456"
    }
    
    try:
        response = requests.post(
            "https://inmuebles-backend-api.onrender.com/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code != 200:
            print(f"Login failed: {response.status_code}")
            return
            
        token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Check properties
        response = requests.get(
            "https://inmuebles-backend-api.onrender.com/properties/",
            headers=headers
        )
        
        if response.status_code == 200:
            properties = response.json()
            print(f"User has {len(properties)} properties")
            
            if len(properties) == 0:
                print("\nFRONTEND WILL REDIRECT TO: /onboarding")
                print("User needs to create properties first")
            else:
                print("\nFRONTEND WILL REDIRECT TO: /financial-agent")
                print("User has properties, can access all features")
                
                for prop in properties:
                    print(f"  - {prop.get('address', 'N/A')} (ID: {prop.get('id')})")
        else:
            print(f"Failed to get properties: {response.status_code}")
            
        # Check viability studies count
        response = requests.get(
            "https://inmuebles-backend-api.onrender.com/viability/",
            headers=headers
        )
        
        if response.status_code == 200:
            studies = response.json()
            print(f"\nViability studies: {len(studies)}")
            print("These should appear after login!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_user_properties()