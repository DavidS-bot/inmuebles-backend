#!/usr/bin/env python3
"""Fix contract end dates from local database"""

import requests
import sqlite3
from pathlib import Path

PROD_API = "https://inmuebles-backend-api.onrender.com"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

def fix_end_dates():
    print("FIXING CONTRACT END DATES")
    print("=" * 40)
    
    # Get local database data
    db_path = Path("data/dev.db")
    if not db_path.exists():
        print("Local database not found")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get contracts with end dates from local DB
    query = """
    SELECT 
        rc.tenant_name,
        rc.end_date,
        rc.is_active,
        p.address
    FROM rentalcontract rc
    JOIN property p ON rc.property_id = p.id
    WHERE rc.end_date IS NOT NULL
    """
    
    cursor.execute(query)
    local_contracts = cursor.fetchall()
    
    print(f"Found {len(local_contracts)} contracts with end dates in local DB")
    
    # Login to production
    response = requests.post(f"{PROD_API}/auth/login", 
                           data={"username": EMAIL, "password": PASSWORD}, timeout=10)
    if response.status_code != 200:
        print("Login failed")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get production contracts
    response = requests.get(f"{PROD_API}/rental-contracts/", headers=headers, timeout=10)
    prod_contracts = response.json()
    
    updated = 0
    
    for local_contract in local_contracts:
        # Find matching production contract by tenant name
        prod_contract = None
        for pc in prod_contracts:
            if local_contract['tenant_name'].lower() in pc['tenant_name'].lower() or pc['tenant_name'].lower() in local_contract['tenant_name'].lower():
                prod_contract = pc
                break
        
        if not prod_contract:
            print(f"No match found for: {local_contract['tenant_name']}")
            continue
        
        # Update with end date
        update_data = {
            "tenant_name": prod_contract['tenant_name'],
            "property_id": prod_contract['property_id'],
            "start_date": prod_contract['start_date'],
            "end_date": local_contract['end_date'],
            "monthly_rent": prod_contract['monthly_rent'],
            "deposit": prod_contract.get('deposit'),
            "is_active": bool(local_contract['is_active'])
        }
        
        try:
            response = requests.put(
                f"{PROD_API}/rental-contracts/{prod_contract['id']}", 
                json=update_data, 
                headers={**headers, "Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                updated += 1
                print(f"Updated: {prod_contract['tenant_name'][:30]:30} | End: {local_contract['end_date']}")
            else:
                print(f"Failed to update {prod_contract['tenant_name']}: {response.status_code}")
                
        except Exception as e:
            print(f"Error updating {prod_contract['tenant_name']}: {str(e)[:50]}")
    
    print(f"\nUpdated {updated} contracts with end dates")
    
    conn.close()

if __name__ == "__main__":
    fix_end_dates()