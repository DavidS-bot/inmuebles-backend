#!/usr/bin/env python3
"""
Test the same API endpoint the frontend uses
"""

import requests

def test_frontend_api():
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
    
    # Test the exact endpoint the frontend uses (no query params)
    print("Testing /financial-movements/ (no filters)...")
    response = requests.get(
        f'{backend_url}/financial-movements/',
        headers=headers,
        timeout=30
    )
    
    if response.status_code != 200:
        print(f"API call failed: {response.status_code}")
        print(response.text)
        return
    
    movements = response.json()
    print(f"Total movements returned: {len(movements)}")
    
    # Check recent movements (2025)
    recent_2025 = [m for m in movements if m.get('date', '').startswith('2025')]
    print(f"2025 movements: {len(recent_2025)}")
    
    # Show the most recent 10
    if recent_2025:
        # Sort by date descending
        recent_2025.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        print("\nMost recent 2025 movements:")
        print("-" * 80)
        print(f"{'ID':<6} {'Date':<12} {'Concept':<40} {'Amount':<12}")
        print("-" * 80)
        
        for movement in recent_2025[:10]:
            concept = movement.get('concept', '')[:37] + "..." if len(movement.get('concept', '')) > 40 else movement.get('concept', '')
            print(f"{movement.get('id', 'N/A'):<6} {movement.get('date', 'N/A'):<12} {concept:<40} {movement.get('amount', 'N/A'):<12}")
    
    # Check specifically for September 2025
    sep_2025 = [m for m in movements if m.get('date', '').startswith('2025-09')]
    print(f"\nSeptember 2025 movements: {len(sep_2025)}")
    
    if sep_2025:
        for movement in sep_2025:
            print(f"  {movement['date']} - {movement['concept']} - {movement['amount']}")

if __name__ == "__main__":
    test_frontend_api()