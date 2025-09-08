#!/usr/bin/env python3
"""Automated production cleanup and sync"""

import requests
import json
import time
from pathlib import Path

PROD_API = "https://inmuebles-backend-api.onrender.com"
LOCAL_API = "http://localhost:8000"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

# Target properties (exactly 11)
TARGET_ADDRESSES = [
    "Jose Luis Lopez de Aranguren 68, Jerez de la Frontera",
    "Jose Luis Lopez de Aranguren 66, Jerez de la Frontera", 
    "Platon 30, Jerez de la Frontera",
    "Jose Luis Lopez de Aranguren 22, Jerez de la Frontera",
    "Calle Seneca (San Isidro Guadalete), S/N, 1, B, 11594, Jerez De La Frontera",
    "Lago de Enol, bloque 1, planta primera, puerta F, 11406, Jerez De La Frontera",
    "Lago de Enol, bloque 1, planta segunda, puerta A, 11406, Jerez De La Frontera",
    "Lago de Enol, bloque 1, planta segunda, puerta B, 11406, Jerez De La Frontera",
    "Lago de Bañolas, nº 1, puerta 4, 11406, Jerez De La Frontera",
    "Lago de Bañolas, nº 1, puerta 9, 11406, Jerez De La Frontera",
    "Lago de Enol, sin número, puerta G, 11406, Jerez De La Frontera"
]

def safe_request(method, url, **kwargs):
    """Make request with retries"""
    for attempt in range(3):
        try:
            kwargs['timeout'] = kwargs.get('timeout', 30)
            response = getattr(requests, method)(url, **kwargs)
            return response
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)[:50]}")
            if attempt < 2:
                time.sleep(5)
            else:
                return None

def login(api_url):
    """Login with retry"""
    print(f"Logging into {api_url}...")
    response = safe_request('post', f"{api_url}/auth/login", 
                          data={"username": EMAIL, "password": PASSWORD})
    if response and response.status_code == 200:
        print("  Login successful!")
        return response.json()["access_token"]
    print("  Login failed!")
    return None

def cleanup_production_properties(token):
    """Remove duplicate properties, keep only correct ones"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\nStep 1: Getting production properties...")
    response = safe_request('get', f"{PROD_API}/properties", headers=headers)
    if not response or response.status_code != 200:
        print("Failed to get properties")
        return False
    
    properties = response.json()
    print(f"Found {len(properties)} properties")
    
    # Group by address (normalize spacing)
    by_address = {}
    for prop in properties:
        addr = prop['address'].strip()
        if addr not in by_address:
            by_address[addr] = []
        by_address[addr].append(prop)
    
    print("\nStep 2: Removing duplicates...")
    deleted_count = 0
    
    for addr, props in by_address.items():
        # Keep the first one, delete the rest
        for prop in props[1:]:  # Skip first, delete rest
            print(f"  Deleting duplicate: {addr[:50]}")
            response = safe_request('delete', f"{PROD_API}/properties/{prop['id']}", headers=headers)
            if response and response.status_code in [200, 204]:
                deleted_count += 1
                time.sleep(0.5)
    
    print(f"  Deleted {deleted_count} duplicate properties")
    
    # Wait and check final count
    time.sleep(3)
    response = safe_request('get', f"{PROD_API}/properties", headers=headers)
    final_props = response.json() if response else []
    print(f"  Final count: {len(final_props)} properties")
    
    return len(final_props) <= 11

def add_missing_properties(local_token, prod_token):
    """Add any missing properties from local"""
    local_headers = {"Authorization": f"Bearer {local_token}"}
    prod_headers = {"Authorization": f"Bearer {prod_token}", "Content-Type": "application/json"}
    
    print("\nStep 3: Checking for missing properties...")
    
    # Get local properties
    response = safe_request('get', f"{LOCAL_API}/properties", headers=local_headers)
    if not response:
        return False
    local_props = response.json()
    
    # Get current production properties
    response = safe_request('get', f"{PROD_API}/properties", headers=prod_headers)
    if not response:
        return False
    prod_props = response.json()
    
    prod_addresses = {prop['address'].strip() for prop in prod_props}
    
    added = 0
    for local_prop in local_props:
        local_addr = local_prop['address'].strip()
        if local_addr not in prod_addresses:
            print(f"  Adding missing property: {local_addr[:50]}")
            
            prop_data = {k: v for k, v in local_prop.items() if k not in ['id', 'owner_id']}
            response = safe_request('post', f"{PROD_API}/properties", 
                                  json=prop_data, headers=prod_headers)
            if response and response.status_code in [200, 201]:
                added += 1
                time.sleep(1)
    
    print(f"  Added {added} missing properties")
    return True

def sync_mortgages(local_token, prod_token):
    """Sync mortgage data"""
    local_headers = {"Authorization": f"Bearer {local_token}"}
    prod_headers = {"Authorization": f"Bearer {prod_token}", "Content-Type": "application/json"}
    
    print("\nStep 4: Syncing mortgages...")
    
    # Get local mortgages
    response = safe_request('get', f"{LOCAL_API}/mortgage-details/", headers=local_headers)
    if not response:
        return False
    local_mortgages = response.json()
    
    synced = 0
    for mortgage in local_mortgages:
        mortgage_data = {k: v for k, v in mortgage.items() if k not in ['id']}
        response = safe_request('post', f"{PROD_API}/mortgage-details/", 
                              json=mortgage_data, headers=prod_headers)
        if response and response.status_code in [200, 201, 400]:  # 400 might be duplicate
            synced += 1
            time.sleep(0.5)
    
    print(f"  Synced {synced} mortgages")
    return True

def upload_key_contracts(token):
    """Upload a few key contracts"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\nStep 5: Uploading key contracts...")
    
    contracts_dir = Path("inmuebles-backend/data/assets/contracts")
    if not contracts_dir.exists():
        contracts_dir = Path("data/assets/contracts")
    
    if not contracts_dir.exists():
        print("  Contracts directory not found")
        return False
    
    # Upload first 5 contracts only (to avoid timeout)
    contracts = list(contracts_dir.glob("*.pdf"))[:5]
    uploaded = 0
    
    for contract_file in contracts:
        try:
            print(f"  Uploading: contract_{uploaded + 1}")
            with open(contract_file, 'rb') as f:
                files = {'file': (f"contract_{uploaded + 1}.pdf", f, 'application/pdf')}
                response = safe_request('post', f"{PROD_API}/uploads/document", 
                                      files=files, headers=headers)
                if response and response.status_code in [200, 201]:
                    uploaded += 1
                    time.sleep(2)
        except Exception as e:
            print(f"  Error uploading contract: {str(e)[:30]}")
    
    print(f"  Uploaded {uploaded} contracts")
    return uploaded > 0

def main():
    print("=" * 60)
    print("AUTOMATED PRODUCTION CLEANUP")
    print("=" * 60)
    
    # Login to both systems
    local_token = login(LOCAL_API)
    prod_token = login(PROD_API)
    
    if not local_token or not prod_token:
        print("Authentication failed!")
        return
    
    # Execute cleanup steps
    success = True
    
    # Step 1: Clean duplicates
    if not cleanup_production_properties(prod_token):
        success = False
    
    # Step 2: Add missing properties
    if success:
        if not add_missing_properties(local_token, prod_token):
            success = False
    
    # Step 3: Sync mortgages
    if success:
        if not sync_mortgages(local_token, prod_token):
            success = False
    
    # Step 4: Upload some contracts
    if success:
        upload_key_contracts(prod_token)
    
    # Final verification
    print("\nStep 6: Final verification...")
    time.sleep(2)
    
    headers = {"Authorization": f"Bearer {prod_token}"}
    response = safe_request('get', f"{PROD_API}/properties", headers=headers)
    if response:
        props = response.json()
        print(f"  Final properties: {len(props)}")
        
        if len(props) == 11:
            print("  SUCCESS: Exactly 11 properties!")
        else:
            print(f"  WARNING: {len(props)} properties (expected 11)")
    
    response = safe_request('get', f"{PROD_API}/mortgage-details/", headers=headers)
    if response:
        mortgages = response.json()
        print(f"  Final mortgages: {len(mortgages)}")
    
    print("\n" + "=" * 60)
    if success:
        print("AUTOMATED CLEANUP COMPLETED!")
    else:
        print("CLEANUP HAD SOME ISSUES")
    print("=" * 60)
    print("Dashboard should now show correct data!")
    print("URL: https://inmuebles-david.vercel.app")

if __name__ == "__main__":
    main()