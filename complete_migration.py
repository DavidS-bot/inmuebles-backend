#!/usr/bin/env python3
"""Complete migration from local to production"""

import requests
import json
import time
from pathlib import Path

LOCAL_API = "http://localhost:8000"
PROD_API = "https://inmuebles-backend-api.onrender.com"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

def login(api_url):
    try:
        response = requests.post(
            f"{api_url}/auth/login",
            data={"username": EMAIL, "password": PASSWORD},
            timeout=15
        )
        return response.json()["access_token"] if response.status_code == 200 else None
    except Exception as e:
        print(f"Login error for {api_url}: {e}")
        return None

def get_all_data(api_url, token):
    """Get ALL data from API"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {}
    
    endpoints = [
        ("properties", "/properties"),
        ("mortgages", "/mortgage-details/"),
        ("contracts", "/rental-contracts"),
        ("movements", "/financial-movements"),
        ("rules", "/classification-rules")
    ]
    
    for name, endpoint in endpoints:
        try:
            response = requests.get(f"{api_url}{endpoint}", headers=headers, timeout=15)
            if response.status_code == 200:
                data[name] = response.json()
                print(f"  {name}: {len(data[name])} records")
            else:
                print(f"  {name}: Failed ({response.status_code})")
                data[name] = []
        except Exception as e:
            print(f"  {name}: Error - {str(e)[:50]}")
            data[name] = []
    
    return data

def delete_all_data(token):
    """Delete ALL data from production"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("Cleaning production database...")
    
    # Get and delete properties (should cascade delete related data)
    try:
        props = requests.get(f"{PROD_API}/properties", headers=headers).json()
        print(f"Deleting {len(props)} properties...")
        for prop in props:
            try:
                requests.delete(f"{PROD_API}/properties/{prop['id']}", headers=headers, timeout=10)
            except:
                pass
    except:
        pass
    
    # Clean remaining data
    cleanup_endpoints = [
        "/mortgage-details/",
        "/rental-contracts",
        "/financial-movements",
        "/classification-rules"
    ]
    
    for endpoint in cleanup_endpoints:
        try:
            items = requests.get(f"{PROD_API}{endpoint}", headers=headers, timeout=10).json()
            if items:
                print(f"Cleaning {len(items)} items from {endpoint}")
                for item in items:
                    try:
                        requests.delete(f"{PROD_API}{endpoint.rstrip('/')}/{item['id']}", headers=headers, timeout=5)
                    except:
                        pass
        except:
            pass
    
    print("Database cleanup completed")

def upload_data(token, local_data):
    """Upload data to production in correct order"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    results = {}
    
    # 1. Upload properties first (required for references)
    print("\n1. Uploading properties...")
    uploaded = 0
    for prop in local_data["properties"]:
        try:
            prop_data = {k: v for k, v in prop.items() if k not in ["id", "owner_id"]}
            response = requests.post(f"{PROD_API}/properties", json=prop_data, headers=headers, timeout=15)
            if response.status_code in [200, 201]:
                uploaded += 1
                print(f"  Property: {prop.get('address', 'Unknown')[:40]}")
            time.sleep(0.5)
        except:
            pass
    results["properties"] = uploaded
    print(f"  -> {uploaded} properties uploaded")
    
    # 2. Upload mortgages
    print("\n2. Uploading mortgages...")
    uploaded = 0
    for mort in local_data["mortgages"]:
        try:
            mort_data = {k: v for k, v in mort.items() if k not in ["id"]}
            response = requests.post(f"{PROD_API}/mortgage-details/", json=mort_data, headers=headers, timeout=15)
            if response.status_code in [200, 201]:
                uploaded += 1
                print(f"  Mortgage for property {mort.get('property_id')}")
            time.sleep(0.5)
        except:
            pass
    results["mortgages"] = uploaded
    print(f"  -> {uploaded} mortgages uploaded")
    
    # 3. Upload contracts
    print("\n3. Uploading rental contracts...")
    uploaded = 0
    for contract in local_data["contracts"]:
        try:
            contract_data = {k: v for k, v in contract.items() if k not in ["id"]}
            response = requests.post(f"{PROD_API}/rental-contracts", json=contract_data, headers=headers, timeout=15)
            if response.status_code in [200, 201]:
                uploaded += 1
                print(f"  Contract: {contract.get('tenant_name', 'Unknown')}")
            time.sleep(0.5)
        except:
            pass
    results["contracts"] = uploaded
    print(f"  -> {uploaded} contracts uploaded")
    
    # 4. Upload classification rules
    print("\n4. Uploading classification rules...")
    uploaded = 0
    for rule in local_data["rules"]:
        try:
            rule_data = {k: v for k, v in rule.items() if k not in ["id"]}
            response = requests.post(f"{PROD_API}/classification-rules", json=rule_data, headers=headers, timeout=15)
            if response.status_code in [200, 201]:
                uploaded += 1
            time.sleep(0.2)
        except:
            pass
    results["rules"] = uploaded
    print(f"  -> {uploaded} rules uploaded")
    
    # 5. Upload financial movements (in batches)
    print("\n5. Uploading financial movements...")
    uploaded = 0
    batch_size = 20
    movements = local_data["movements"]
    
    for i in range(0, len(movements), batch_size):
        batch = movements[i:i+batch_size]
        print(f"  Batch {i//batch_size + 1}: {len(batch)} movements")
        
        for movement in batch:
            try:
                mov_data = {k: v for k, v in movement.items() if k not in ["id"]}
                response = requests.post(f"{PROD_API}/financial-movements", json=mov_data, headers=headers, timeout=10)
                if response.status_code in [200, 201]:
                    uploaded += 1
            except:
                pass
        time.sleep(1)  # Pause between batches
    
    results["movements"] = uploaded
    print(f"  -> {uploaded} movements uploaded")
    
    return results

def main():
    print("=" * 60)
    print("COMPLETE MIGRATION: LOCAL -> PRODUCTION")
    print("=" * 60)
    
    # Get tokens
    print("\nStep 1: Authentication...")
    local_token = login(LOCAL_API)
    prod_token = login(PROD_API)
    
    if not local_token:
        print("Cannot connect to local backend")
        return
    if not prod_token:
        print("Cannot connect to production backend")
        return
    
    print("Authentication successful!")
    
    # Get all local data
    print("\nStep 2: Exporting from local...")
    local_data = get_all_data(LOCAL_API, local_token)
    
    if len(local_data["properties"]) != 11:
        print(f"WARNING: Expected 11 properties, found {len(local_data['properties'])}")
    
    # Clean production
    print("\nStep 3: Cleaning production...")
    delete_all_data(prod_token)
    
    # Wait for cleanup
    time.sleep(3)
    
    # Upload to production
    print("\nStep 4: Uploading to production...")
    results = upload_data(prod_token, local_data)
    
    # Verify
    print("\nStep 5: Verification...")
    time.sleep(2)
    prod_data = get_all_data(PROD_API, prod_token)
    
    print("\n" + "=" * 60)
    print("MIGRATION SUMMARY")
    print("=" * 60)
    print(f"Properties: {results.get('properties', 0)} uploaded -> {len(prod_data['properties'])} final")
    print(f"Mortgages: {results.get('mortgages', 0)} uploaded -> {len(prod_data['mortgages'])} final")
    print(f"Contracts: {results.get('contracts', 0)} uploaded -> {len(prod_data['contracts'])} final")
    print(f"Rules: {results.get('rules', 0)} uploaded -> {len(prod_data['rules'])} final")
    print(f"Movements: {results.get('movements', 0)} uploaded -> {len(prod_data['movements'])} final")
    
    if len(prod_data["properties"]) == 11:
        print("\nSUCCESS: Exactly 11 properties in production!")
    else:
        print(f"\nWARNING: {len(prod_data['properties'])} properties instead of 11")
    
    print("\nMigration completed!")

if __name__ == "__main__":
    main()