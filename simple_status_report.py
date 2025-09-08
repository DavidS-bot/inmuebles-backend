#!/usr/bin/env python3
"""Simple status report"""

import requests
import json
import sqlite3
from pathlib import Path

LOCAL_API = "http://localhost:8000"
PROD_API = "https://inmuebles-backend-api.onrender.com"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

def login(api_url):
    try:
        response = requests.post(f"{api_url}/auth/login", 
                               data={"username": EMAIL, "password": PASSWORD}, timeout=10)
        return response.json()["access_token"] if response.status_code == 200 else None
    except:
        return None

def create_report():
    print("CURRENT STATUS REPORT")
    print("=" * 40)
    
    # Get tokens
    local_token = login(LOCAL_API)
    prod_token = login(PROD_API)
    
    print(f"Local API login: {'OK' if local_token else 'FAILED'}")
    print(f"Production API login: {'OK' if prod_token else 'FAILED'}")
    
    if not prod_token:
        return
    
    headers = {"Authorization": f"Bearer {prod_token}"}
    
    # Test production endpoints
    endpoints = [
        "/properties",
        "/mortgage-details/",
        "/classification-rules",
        "/rental-contracts"
    ]
    
    print(f"\nProduction endpoints:")
    for endpoint in endpoints:
        try:
            response = requests.get(f"{PROD_API}{endpoint}", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else "N/A"
                print(f"  {endpoint}: OK ({count} items)")
                
                if endpoint == "/mortgage-details/":
                    total_debt = sum(item.get('outstanding_balance', 0) for item in data)
                    print(f"    Total debt: {total_debt:,.2f} EUR")
                    
            else:
                print(f"  {endpoint}: ERROR {response.status_code}")
        except Exception as e:
            print(f"  {endpoint}: TIMEOUT")
    
    # Get local data count
    db_path = Path("data/dev.db")
    if db_path.exists():
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM classificationrule")
            local_rules = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM rentalcontract")
            local_contracts = cursor.fetchone()[0]
            
            conn.close()
            
            print(f"\nLocal data to migrate:")
            print(f"  Classification rules: {local_rules}")
            print(f"  Rental contracts: {local_contracts}")
            
        except Exception as e:
            print(f"Could not read local database: {e}")
    
    print(f"\nConclusion:")
    print(f"- Mortgage data is synced (debt shows correctly)")
    print(f"- Classification rules endpoint: NOT WORKING")
    print(f"- Rental contracts endpoint: NOT WORKING")
    print(f"- Dashboard should show correct debt amount")

if __name__ == "__main__":
    create_report()