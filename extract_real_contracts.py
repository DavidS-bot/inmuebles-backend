#!/usr/bin/env python3
"""Extract real contract data"""

import sqlite3
import json
from pathlib import Path

def extract_contracts():
    # Connect to local database
    conn = sqlite3.connect("data/dev.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all rental contracts with property info
    query = """
    SELECT 
        rc.tenant_name,
        rc.monthly_rent,
        rc.deposit,
        rc.start_date,
        rc.is_active,
        rc.contract_file_name,
        p.address
    FROM rentalcontract rc
    JOIN property p ON rc.property_id = p.id
    ORDER BY p.address
    """
    
    cursor.execute(query)
    contracts = cursor.fetchall()
    
    print(f"CONTRACTS FROM LOCAL DB: {len(contracts)}")
    print("-" * 50)
    
    data = []
    for c in contracts:
        contract_info = {
            "tenant": c['tenant_name'],
            "rent": float(c['monthly_rent']),
            "deposit": float(c['deposit']),
            "start": c['start_date'],
            "active": bool(c['is_active']),
            "property": c['address'],
            "pdf": c['contract_file_name']
        }
        data.append(contract_info)
        
        # Print simplified info
        short_addr = c['address'].split(',')[0] if ',' in c['address'] else c['address'][:30]
        print(f"{short_addr[:30]:30} | {c['tenant_name'][:40]:40} | {c['monthly_rent']:7.0f} EUR")
    
    # Save to JSON
    with open("real_contracts.json", "w", encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved {len(data)} contracts to real_contracts.json")
    
    conn.close()

if __name__ == "__main__":
    extract_contracts()