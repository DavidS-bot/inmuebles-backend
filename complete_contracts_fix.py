#!/usr/bin/env python3
"""Complete fix for rental contracts"""

import requests
import json
from pathlib import Path

PROD_API = "https://inmuebles-backend-api.onrender.com"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

def main():
    print("COMPLETE CONTRACT FIX")
    print("=" * 40)
    
    # Login
    response = requests.post(f"{PROD_API}/auth/login", 
                           data={"username": EMAIL, "password": PASSWORD}, timeout=10)
    if response.status_code != 200:
        print("Login failed")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login OK")
    
    # Step 1: Delete all existing contracts
    print("\n1. DELETING EXISTING CONTRACTS:")
    response = requests.get(f"{PROD_API}/rental-contracts/", headers=headers, timeout=10)
    if response.status_code == 200:
        existing = response.json()
        print(f"   Found {len(existing)} contracts to delete")
        
        for contract in existing:
            response = requests.delete(f"{PROD_API}/rental-contracts/{contract['id']}", 
                                     headers=headers, timeout=10)
            if response.status_code in [200, 204]:
                print(f"   Deleted: {contract['tenant_name']}")
    
    # Step 2: Get properties for mapping
    print("\n2. GETTING PROPERTIES:")
    response = requests.get(f"{PROD_API}/properties", headers=headers, timeout=10)
    properties = response.json()
    print(f"   Found {len(properties)} properties")
    
    # Create mapping dictionary
    prop_map = {}
    for prop in properties:
        addr = prop['address'].lower()
        # Map each property
        if "aranguren 68" in addr or "aranguren, 68" in addr:
            prop_map["aranguren_68"] = prop['id']
        elif "aranguren 66" in addr or "aranguren, 66" in addr:
            prop_map["aranguren_66"] = prop['id']
        elif "aranguren 22" in addr or "aranguren, 22" in addr:
            prop_map["aranguren_22"] = prop['id']
        elif "platon" in addr:
            prop_map["platon_30"] = prop['id']
        elif "seneca" in addr:
            prop_map["pozoalbero"] = prop['id']
        elif "lago" in addr:
            if "puerta f" in addr:
                prop_map["lago_f"] = prop['id']
            elif "segunda" in addr and "puerta a" in addr:
                prop_map["lago_a"] = prop['id']
            elif "segunda" in addr and "puerta b" in addr:
                prop_map["lago_b"] = prop['id']
            elif "puerta 4" in addr:
                prop_map["lago_4"] = prop['id']
            elif "puerta 9" in addr:
                prop_map["lago_9"] = prop['id']
            elif "puerta g" in addr:
                prop_map["lago_g"] = prop['id']
    
    # Step 3: Load real contracts data
    print("\n3. LOADING REAL CONTRACT DATA:")
    with open("real_contracts.json", "r", encoding='utf-8') as f:
        real_contracts = json.load(f)
    print(f"   Loaded {len(real_contracts)} contracts")
    
    # Step 4: Upload correct contracts
    print("\n4. UPLOADING CORRECT CONTRACTS:")
    uploaded = 0
    
    for contract in real_contracts:
        # Map property
        property_id = None
        prop_addr = contract['property'].lower()
        
        if "aranguren 68" in prop_addr:
            property_id = prop_map.get("aranguren_68")
        elif "aranguren 66" in prop_addr:
            property_id = prop_map.get("aranguren_66")
        elif "aranguren 22" in prop_addr or "aranguren, 22" in prop_addr:
            property_id = prop_map.get("aranguren_22")
        elif "platon" in prop_addr:
            property_id = prop_map.get("platon_30")
        elif "seneca" in prop_addr:
            property_id = prop_map.get("pozoalbero")
        elif "lago" in prop_addr:
            # Match specific Lago properties
            if "puerta f" in prop_addr or "planta primera" in prop_addr:
                property_id = prop_map.get("lago_f")
            elif "planta segunda, puerta a" in prop_addr:
                property_id = prop_map.get("lago_a")
            elif "planta segunda, puerta b" in prop_addr:
                property_id = prop_map.get("lago_b")
            elif "puerta 4" in prop_addr or "bajo" in prop_addr:
                property_id = prop_map.get("lago_4")
            elif "puerta 9" in prop_addr:
                property_id = prop_map.get("lago_9")
            elif "puerta g" in prop_addr or "sin numero" in prop_addr:
                property_id = prop_map.get("lago_g")
        
        if not property_id:
            print(f"   WARNING: No property match for: {contract['property'][:50]}")
            continue
        
        # Create contract
        contract_data = {
            "property_id": property_id,
            "tenant_name": contract['tenant'],
            "start_date": contract['start'],
            "end_date": None,
            "monthly_rent": contract['rent'],
            "deposit": contract['deposit'],
            "is_active": contract['active']
        }
        
        # Upload
        headers_post = {**headers, "Content-Type": "application/json"}
        response = requests.post(f"{PROD_API}/rental-contracts/", 
                               json=contract_data, headers=headers_post, timeout=15)
        
        if response.status_code in [200, 201]:
            uploaded += 1
            print(f"   OK: {contract['tenant'][:40]:40} | {contract['rent']:7.0f} EUR")
        else:
            print(f"   FAIL: {contract['tenant'][:40]} - {response.status_code}")
    
    print(f"\n   Total uploaded: {uploaded}/{len(real_contracts)}")
    
    # Step 5: Final check
    print("\n5. FINAL CHECK:")
    response = requests.get(f"{PROD_API}/rental-contracts/", headers=headers, timeout=10)
    if response.status_code == 200:
        final = response.json()
        print(f"   Total contracts in system: {len(final)}")
        
        # Show summary by property
        by_prop = {}
        for c in final:
            prop_id = c['property_id']
            if prop_id not in by_prop:
                by_prop[prop_id] = []
            by_prop[prop_id].append((c['tenant_name'], c['monthly_rent']))
        
        print("\n   Contracts by property:")
        for prop_id, contracts in by_prop.items():
            # Get property address
            prop_addr = next((p['address'] for p in properties if p['id'] == prop_id), f"Property {prop_id}")
            print(f"\n   {prop_addr[:50]}:")
            for tenant, rent in contracts:
                print(f"      - {tenant[:40]:40} | {rent:7.0f} EUR")
    
    print("\n" + "=" * 40)
    print("Contract data fixed. Next step: Upload PDFs")

if __name__ == "__main__":
    main()