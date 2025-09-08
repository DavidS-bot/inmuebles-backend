#!/usr/bin/env python3
"""
Debug frontend data loading by simulating the exact same calls
"""

import requests
from datetime import datetime

def debug_frontend_loading():
    """Simulate exact frontend API calls"""
    
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    # Simulate login (same as frontend)
    login_data = {'username': 'davsanchez21277@gmail.com', 'password': '123456'}
    
    print("Step 1: Login...")
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
    
    print("Login successful")
    
    # Simulate exact frontend API calls
    print("\nStep 2: Load properties...")
    try:
        properties_res = requests.get(f'{backend_url}/properties', headers=headers, timeout=30)
        properties_data = properties_res.data if properties_res.status_code == 200 else []
        print(f"Properties loaded: {len(properties_data) if properties_data else 0}")
    except Exception as e:
        print(f"Properties endpoint not available: {e}")
        properties_data = []
    
    # Load movements (exact same endpoint as frontend)
    print("\nStep 3: Load movements...")
    movements_url = f'{backend_url}/financial-movements/'
    
    print(f"Calling: {movements_url}")
    movements_res = requests.get(movements_url, headers=headers, timeout=30)
    
    if movements_res.status_code != 200:
        print(f"Movements API failed: {movements_res.status_code}")
        return
    
    movements = movements_res.json()
    print(f"Movements loaded: {len(movements)} total")
    
    # Sort by date descending (same as frontend should do)
    print("\nStep 4: Sort by date...")
    def parse_date(date_str):
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except:
            return datetime.min
    
    sorted_movements = sorted(movements, key=lambda x: parse_date(x.get('date', '')), reverse=True)
    
    print("First 10 movements after sorting:")
    print("-" * 80)
    print(f"{'ID':<6} {'Date':<12} {'Concept':<40} {'Amount':<12}")
    print("-" * 80)
    
    for i, movement in enumerate(sorted_movements[:10], 1):
        concept = movement.get('concept', '')[:37] + "..." if len(movement.get('concept', '')) > 40 else movement.get('concept', '')
        print(f"{movement.get('id', 'N/A'):<6} {movement.get('date', 'N/A'):<12} {concept:<40} {movement.get('amount', 'N/A'):<12}")
    
    # Check September 2025 specifically
    sep_2025 = [m for m in movements if m.get('date', '').startswith('2025-09')]
    print(f"\nSeptember 2025 movements: {len(sep_2025)}")
    
    if sep_2025:
        print("September movements details:")
        for movement in sep_2025:
            print(f"  ID {movement['id']}: {movement['date']} - {movement['concept']} - {movement['amount']}")
    
    # Check if there are any recent movements at all
    recent_2025 = [m for m in movements if m.get('date', '').startswith('2025')]
    print(f"\nTotal 2025 movements: {len(recent_2025)}")
    
    # Show date range
    if recent_2025:
        dates = [m['date'] for m in recent_2025 if m.get('date')]
        dates.sort()
        print(f"Date range: {dates[0]} to {dates[-1]}")

if __name__ == "__main__":
    debug_frontend_loading()