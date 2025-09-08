#!/usr/bin/env python3
"""Test actual deletion to see the exact error"""

import requests
import json

def test_actual_deletion():
    print("Testing actual movement deletion...")
    
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
        
        # Get movements to find a specific unassigned one
        movements_response = requests.get(
            'https://inmuebles-backend-api.onrender.com/financial-movements/?limit=100',
            headers=headers,
            timeout=15
        )
        
        if movements_response.status_code != 200:
            print(f"Failed to get movements: {movements_response.status_code}")
            return
            
        movements = movements_response.json()
        print(f"Found {len(movements)} movements")
        
        # Find the specific movement mentioned: "TRANSF OTRAS LUCIA MARIN CHIA"
        target_movement = None
        for movement in movements:
            if "LUCIA MARIN CHIA" in movement.get('concept', ''):
                target_movement = movement
                break
                
        if not target_movement:
            print("Target movement 'LUCIA MARIN CHIA' not found")
            # Find any unassigned movement
            for movement in movements:
                if movement.get('property_id') is None:
                    target_movement = movement
                    break
                    
        if not target_movement:
            print("No unassigned movements found")
            return
            
        movement_id = target_movement['id']
        print(f"Testing deletion of movement ID: {movement_id}")
        print(f"Property ID: {target_movement.get('property_id')}")
        print(f"Concept: {target_movement.get('concept', '')}")
        print(f"Amount: {target_movement.get('amount', 0)}")
        
        # ACTUALLY try to delete it to see the exact error
        print("\nAttempting deletion...")
        delete_response = requests.delete(
            f'https://inmuebles-backend-api.onrender.com/financial-movements/{movement_id}',
            headers=headers,
            timeout=15
        )
        
        print(f"Delete response status: {delete_response.status_code}")
        print(f"Delete response text: {delete_response.text}")
        
        if delete_response.status_code == 200:
            print("✅ Deletion successful!")
        else:
            print(f"❌ Deletion failed: {delete_response.status_code}")
            try:
                error_data = delete_response.json()
                print(f"Error detail: {error_data}")
            except:
                pass
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_actual_deletion()