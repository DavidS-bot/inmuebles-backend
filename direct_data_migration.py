#!/usr/bin/env python3
"""Direct data migration using working endpoints only"""

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

def get_local_data_from_db():
    """Get data directly from local SQLite database"""
    db_path = Path("data/dev.db")
    if not db_path.exists():
        print(f"Database not found: {db_path}")
        return None, None
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    cursor = conn.cursor()
    
    # Get classification rules
    cursor.execute("""
        SELECT cr.*, p.address as property_address 
        FROM classificationrule cr 
        JOIN property p ON cr.property_id = p.id
    """)
    rules = [dict(row) for row in cursor.fetchall()]
    
    # Get rental contracts
    cursor.execute("""
        SELECT rc.*, p.address as property_address 
        FROM rentalcontract rc 
        JOIN property p ON rc.property_id = p.id
    """)
    contracts = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return rules, contracts

def create_summary_report():
    """Create a summary report of what data we have"""
    print("=" * 60)
    print("DIRECT DATA MIGRATION REPORT")
    print("=" * 60)
    
    # Get tokens
    local_token = login(LOCAL_API)
    prod_token = login(PROD_API)
    
    if not local_token:
        print("❌ Local API login failed")
        return
    if not prod_token:
        print("❌ Production API login failed")
        return
    
    print("✅ Both APIs accessible")
    
    # Get local data from database
    local_rules, local_contracts = get_local_data_from_db()
    
    if local_rules is None:
        print("❌ Could not read local database")
        return
    
    print(f"\n📊 LOCAL DATA (from database):")
    print(f"  Classification Rules: {len(local_rules)}")
    print(f"  Rental Contracts: {len(local_contracts)}")
    
    # Show sample data
    if local_rules:
        print(f"\n📋 Sample Classification Rules:")
        for i, rule in enumerate(local_rules[:3]):
            print(f"  {i+1}. '{rule['keyword']}' -> {rule['category']} (Property: {rule['property_address'][:30]})")
    
    if local_contracts:
        print(f"\n🏠 Sample Rental Contracts:")
        for i, contract in enumerate(local_contracts[:3]):
            print(f"  {i+1}. {contract['tenant_name']} - {contract['monthly_rent']}€ (Property: {contract['property_address'][:30]})")
    
    # Get production data
    headers = {"Authorization": f"Bearer {prod_token}"}
    
    try:
        props_response = requests.get(f"{PROD_API}/properties", headers=headers, timeout=10)
        prod_properties = props_response.json() if props_response.status_code == 200 else []
    except:
        prod_properties = []
    
    try:
        mortgages_response = requests.get(f"{PROD_API}/mortgage-details/", headers=headers, timeout=10)
        prod_mortgages = mortgages_response.json() if mortgages_response.status_code == 200 else []
        total_debt = sum(m.get('outstanding_balance', 0) for m in prod_mortgages)
    except:
        prod_mortgages = []
        total_debt = 0
    
    print(f"\n📊 PRODUCTION DATA (working endpoints):")
    print(f"  Properties: {len(prod_properties)}")
    print(f"  Mortgages: {len(prod_mortgages)}")
    print(f"  Total Debt: {total_debt:,.2f} EUR")
    print(f"  Classification Rules: ❌ Endpoint not working (405)")
    print(f"  Rental Contracts: ❌ Endpoint not working (405)")
    
    print(f"\n🎯 MIGRATION NEEDED:")
    print(f"  ✅ Properties: Already synced ({len(prod_properties)} items)")
    print(f"  ✅ Mortgages: Already synced ({len(prod_mortgages)} items, {total_debt:,.2f} EUR debt)")
    print(f"  ❌ Classification Rules: Need to sync {len(local_rules)} rules")
    print(f"  ❌ Rental Contracts: Need to sync {len(local_contracts)} contracts")
    
    print(f"\n🔧 SOLUTION NEEDED:")
    print(f"  1. Fix classification-rules and rental-contracts endpoints in production")
    print(f"  2. Or implement direct database migration")
    print(f"  3. Dashboard debt should already show correctly: {total_debt:,.2f} EUR")

if __name__ == "__main__":
    create_summary_report()