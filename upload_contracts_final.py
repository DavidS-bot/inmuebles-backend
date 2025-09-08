#!/usr/bin/env python3
"""Upload all rental contracts with correct tenant names - simple version"""

import requests
from datetime import date

PROD_API = "https://inmuebles-backend-api.onrender.com"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

# Simplified contract data with correct tenant names
CONTRACTS = [
    {"tenant": "Rocio", "property_match": "aranguren 68", "rent": 650},
    {"tenant": "Susana y Jorge", "property_match": "aranguren 66", "rent": 650},
    {"tenant": "Alvaro", "property_match": "aranguren 22", "rent": 550},
    {"tenant": "J. Antonio y Maria", "property_match": "aranguren 22", "rent": 550},
    {"tenant": "Antonio y Olga", "property_match": "platon", "rent": 700},
    {"tenant": "Diego y Soledad", "property_match": "platon", "rent": 700},
    {"tenant": "Leandro Emanuel", "property_match": "seneca", "rent": 600},
    {"tenant": "Sergio Bravo", "property_match": "seneca", "rent": 600},
    {"tenant": "Judit y Jesus", "property_match": "lago de enol", "rent": 650},
    {"tenant": "Antonio", "property_match": "lago de enol", "rent": 650},
    {"tenant": "Roberto y Kerthyns", "property_match": "lago de enol", "rent": 650},
    {"tenant": "Manuela", "property_match": "lago de enol", "rent": 650},
    {"tenant": "Jesus Javier y Carolina", "property_match": "lago de enol", "rent": 650},
    {"tenant": "Lucia", "property_match": "lago de enol", "rent": 650},
    {"tenant": "Manuel Orellana", "property_match": "lago de enol", "rent": 650},
    {"tenant": "Eva y Manuel", "property_match": "lago de enol", "rent": 650}
]

def main():
    print("UPLOADING RENTAL CONTRACTS")
    print("=" * 30)
    
    # Login
    response = requests.post(f"{PROD_API}/auth/login", 
                           data={"username": EMAIL, "password": PASSWORD}, timeout=10)
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login OK")
    
    # Get properties
    response = requests.get(f"{PROD_API}/properties", headers=headers, timeout=10)
    if response.status_code != 200:
        print("Failed to get properties")
        return
    
    properties = response.json()
    print(f"Properties: {len(properties)}")
    
    # Get existing contracts
    response = requests.get(f"{PROD_API}/rental-contracts/", headers=headers, timeout=10)
    existing = response.json() if response.status_code == 200 else []
    existing_tenants = [c['tenant_name'].lower() for c in existing]
    print(f"Existing contracts: {len(existing)}")
    
    # Upload contracts
    uploaded = 0
    skipped = 0
    
    for contract in CONTRACTS:
        tenant = contract["tenant"]
        
        # Skip if exists
        if tenant.lower() in existing_tenants:
            print(f"  Skip: {tenant} (exists)")
            skipped += 1
            continue
        
        # Find matching property
        property_id = None
        for prop in properties:
            if contract["property_match"].lower() in prop['address'].lower():
                property_id = prop['id']
                break
        
        if not property_id:
            print(f"  No property for: {tenant}")
            continue
        
        # Create contract
        contract_data = {
            "property_id": property_id,
            "tenant_name": tenant,
            "start_date": "2024-01-01",
            "end_date": None,
            "monthly_rent": contract["rent"],
            "deposit": contract["rent"] * 2,
            "is_active": True
        }
        
        try:
            headers_post = {**headers, "Content-Type": "application/json"}
            response = requests.post(f"{PROD_API}/rental-contracts/", 
                                   json=contract_data, headers=headers_post, timeout=15)
            
            if response.status_code in [200, 201]:
                uploaded += 1
                print(f"  OK: {tenant}")
            else:
                print(f"  FAIL: {tenant} ({response.status_code})")
                
        except Exception as e:
            print(f"  ERROR: {tenant} - {str(e)[:30]}")
    
    print(f"\nSUMMARY:")
    print(f"  Uploaded: {uploaded}")
    print(f"  Skipped: {skipped}")
    
    # Final check
    response = requests.get(f"{PROD_API}/rental-contracts/", headers=headers, timeout=10)
    if response.status_code == 200:
        final = response.json()
        print(f"\nTotal contracts now: {len(final)}")
        print("\nAll tenants:")
        for c in final:
            print(f"  - {c['tenant_name']}")

if __name__ == "__main__":
    main()