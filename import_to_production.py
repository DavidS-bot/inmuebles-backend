#!/usr/bin/env python3
"""Import ALL data to production backend"""

import requests
import json
import time
from pathlib import Path

PROD_API = "https://inmuebles-backend-api.onrender.com"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

def get_token():
    try:
        response = requests.post(
            f"{PROD_API}/auth/login",
            data={"username": EMAIL, "password": PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()["access_token"]
    except Exception as e:
        print(f"Login error: {e}")
    return None

def import_properties(token, properties):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    imported = 0
    
    for prop in properties:
        try:
            # Remove id for creation
            prop_data = {k: v for k, v in prop.items() if k != "id"}
            response = requests.post(f"{PROD_API}/properties", json=prop_data, headers=headers, timeout=30)
            if response.status_code in [200, 201]:
                imported += 1
                print(f"  Property '{prop.get('address', 'Unknown')}' imported")
            else:
                print(f"  Failed: {prop.get('address', 'Unknown')} - {response.status_code}")
        except Exception as e:
            print(f"  Error: {str(e)[:50]}")
        time.sleep(1)  # Avoid rate limiting
    
    return imported

def import_mortgages(token, mortgages):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    imported = 0
    
    for mortgage in mortgages:
        try:
            # Remove id for creation
            mortgage_data = {k: v for k, v in mortgage.items() if k != "id"}
            response = requests.post(f"{PROD_API}/mortgage-details/", json=mortgage_data, headers=headers, timeout=30)
            if response.status_code in [200, 201]:
                imported += 1
                print(f"  Mortgage for property {mortgage.get('property_id')} imported")
            else:
                print(f"  Failed mortgage: {response.status_code}")
        except Exception as e:
            print(f"  Error: {str(e)[:50]}")
        time.sleep(1)
    
    return imported

def import_contracts(token, contracts):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    imported = 0
    
    for contract in contracts:
        try:
            # Remove id for creation
            contract_data = {k: v for k, v in contract.items() if k != "id"}
            response = requests.post(f"{PROD_API}/rental-contracts", json=contract_data, headers=headers, timeout=30)
            if response.status_code in [200, 201]:
                imported += 1
                print(f"  Contract for '{contract.get('tenant_name', 'Unknown')}' imported")
            else:
                print(f"  Failed contract: {response.status_code}")
        except Exception as e:
            print(f"  Error: {str(e)[:50]}")
        time.sleep(1)
    
    return imported

def import_movements(token, movements):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    imported = 0
    batch_size = 50
    
    # Import in batches to avoid overwhelming the server
    for i in range(0, len(movements), batch_size):
        batch = movements[i:i+batch_size]
        print(f"  Importing batch {i//batch_size + 1} ({len(batch)} movements)...")
        
        for movement in batch:
            try:
                # Remove id for creation
                movement_data = {k: v for k, v in movement.items() if k != "id"}
                response = requests.post(f"{PROD_API}/financial-movements", json=movement_data, headers=headers, timeout=30)
                if response.status_code in [200, 201]:
                    imported += 1
            except:
                pass
        
        time.sleep(2)  # Pause between batches
    
    return imported

def import_rules(token, rules):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    imported = 0
    
    for rule in rules:
        try:
            # Remove id for creation
            rule_data = {k: v for k, v in rule.items() if k != "id"}
            response = requests.post(f"{PROD_API}/classification-rules", json=rule_data, headers=headers, timeout=30)
            if response.status_code in [200, 201]:
                imported += 1
                print(f"  Rule '{rule.get('rule_name', 'Unknown')}' imported")
        except:
            pass
        time.sleep(0.5)
    
    return imported

def main():
    print("=" * 50)
    print("PRODUCTION DATA IMPORT")
    print("=" * 50)
    
    # Load exported data
    export_files = list(Path(".").glob("local_data_export_*.json"))
    if not export_files:
        print("No export file found!")
        return
    
    latest_export = sorted(export_files)[-1]
    print(f"Loading data from: {latest_export}")
    
    with open(latest_export, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Authenticate
    token = get_token()
    if not token:
        print("Failed to authenticate with production backend")
        return
    
    print("Authentication successful!")
    print("\nStarting import to production...")
    
    # Import properties first (required for references)
    print(f"\n1. Importing {len(data.get('properties', []))} properties...")
    props_imported = import_properties(token, data.get('properties', []))
    print(f"   -> {props_imported} properties imported")
    
    # Import mortgages
    print(f"\n2. Importing {len(data.get('mortgages', []))} mortgages...")
    morts_imported = import_mortgages(token, data.get('mortgages', []))
    print(f"   -> {morts_imported} mortgages imported")
    
    # Import contracts
    print(f"\n3. Importing {len(data.get('contracts', []))} rental contracts...")
    conts_imported = import_contracts(token, data.get('contracts', []))
    print(f"   -> {conts_imported} contracts imported")
    
    # Import movements (this may take a while)
    print(f"\n4. Importing {len(data.get('movements', []))} financial movements...")
    movs_imported = import_movements(token, data.get('movements', []))
    print(f"   -> {movs_imported} movements imported")
    
    # Import rules
    print(f"\n5. Importing {len(data.get('rules', []))} classification rules...")
    rules_imported = import_rules(token, data.get('rules', []))
    print(f"   -> {rules_imported} rules imported")
    
    print("\n" + "=" * 50)
    print("IMPORT SUMMARY")
    print("=" * 50)
    print(f"Properties: {props_imported}")
    print(f"Mortgages: {morts_imported}")
    print(f"Contracts: {conts_imported}")
    print(f"Movements: {movs_imported}")
    print(f"Rules: {rules_imported}")
    print("\nImport completed!")

if __name__ == "__main__":
    main()