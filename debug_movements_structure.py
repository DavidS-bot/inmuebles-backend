#!/usr/bin/env python3
"""
Debug the structure of movements in production
"""

import requests
import json

def debug_movements():
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
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
    
    # Get movements
    response = requests.get(
        f'{backend_url}/financial-movements/',
        headers=headers,
        timeout=30
    )
    
    if response.status_code != 200:
        print(f"Failed to get movements: {response.status_code}")
        return
    
    movements = response.json()
    
    print(f"Total movements: {len(movements)}")
    
    # Check the last 10 movements structure
    print("\nLast 10 movements structure:")
    for i, movement in enumerate(movements[-10:], 1):
        print(f"\n=== Movement {len(movements) - 10 + i} (ID: {movement.get('id')}) ===")
        print(json.dumps(movement, indent=2, default=str))
        
    # Look for any movements with data
    movements_with_data = []
    for movement in movements:
        if (movement.get('fecha') and movement.get('fecha') != 'N/A' and 
            movement.get('concepto') and movement.get('importe') is not None):
            movements_with_data.append(movement)
    
    print(f"\nMovements with actual data: {len(movements_with_data)}")
    
    if movements_with_data:
        print("\nSample movement with data:")
        sample = movements_with_data[-1]  # Most recent with data
        print(json.dumps(sample, indent=2, default=str))

if __name__ == "__main__":
    debug_movements()