#!/usr/bin/env python3
"""
Check production database for recent movements
"""

import requests
import pandas as pd
from datetime import datetime

def check_production_movements():
    """Check if the recent movements are in production"""
    
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    # Login first
    login_data = {'username': 'davsanchez21277@gmail.com', 'password': '123456'}
    response = requests.post(
        f'{backend_url}/auth/login',
        data=login_data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        timeout=30
    )
    
    if response.status_code != 200:
        print(f"ERROR Login failed: {response.status_code}")
        return
    
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Get recent movements
    print("Checking production movements...")
    response = requests.get(
        f'{backend_url}/financial-movements/',
        headers=headers,
        timeout=30
    )
    
    if response.status_code != 200:
        print(f"ERROR Failed to get movements: {response.status_code}")
        return
    
    movements = response.json()
    
    print(f"SUCCESS Total movements in production: {len(movements)}")
    
    # Filter recent movements (August and September 2025)
    recent_movements = []
    for movement in movements:
        try:
            # Parse date
            if 'fecha' in movement:
                date_str = movement['fecha']
                # Try different date formats
                for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']:
                    try:
                        date_obj = datetime.strptime(date_str, fmt)
                        if date_obj.year == 2025 and date_obj.month in [8, 9]:
                            recent_movements.append({
                                'id': movement.get('id'),
                                'fecha': date_str,
                                'concepto': movement.get('concepto', ''),
                                'importe': movement.get('importe', 0),
                                'date_obj': date_obj
                            })
                        break
                    except:
                        continue
        except Exception as e:
            continue
    
    # Sort by date descending
    recent_movements.sort(key=lambda x: x['date_obj'], reverse=True)
    
    print(f"\nRecent movements (August-September 2025): {len(recent_movements)}")
    
    if recent_movements:
        print("\nMost recent movements:")
        print("-" * 80)
        print(f"{'ID':<5} {'Fecha':<12} {'Concepto':<40} {'Importe':<15}")
        print("-" * 80)
        
        for i, movement in enumerate(recent_movements[:20]):  # Show top 20
            concepto = movement['concepto'][:37] + "..." if len(movement['concepto']) > 40 else movement['concepto']
            print(f"{movement['id']:<5} {movement['fecha']:<12} {concepto:<40} {movement['importe']:<15}")
        
        # Count by month
        aug_count = sum(1 for m in recent_movements if m['date_obj'].month == 8)
        sep_count = sum(1 for m in recent_movements if m['date_obj'].month == 9)
        
        print(f"\nMonthly distribution:")
        print(f"   Agosto 2025: {aug_count} movimientos")
        print(f"   Septiembre 2025: {sep_count} movimientos")
        
    else:
        print("WARNING No recent movements found for August-September 2025")
        
        # Show the most recent movements regardless of date
        print("\nMost recent movements (any date):")
        if movements:
            print("-" * 80)
            print(f"{'ID':<5} {'Fecha':<12} {'Concepto':<40} {'Importe':<15}")
            print("-" * 80)
            
            for i, movement in enumerate(movements[:10]):
                concepto = movement.get('concepto', '')[:37] + "..." if len(movement.get('concepto', '')) > 40 else movement.get('concepto', '')
                print(f"{movement.get('id', 'N/A'):<5} {movement.get('fecha', 'N/A'):<12} {concepto:<40} {movement.get('importe', 'N/A'):<15}")

if __name__ == "__main__":
    check_production_movements()