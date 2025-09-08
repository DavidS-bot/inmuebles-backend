#!/usr/bin/env python3
"""Upload all rental contracts with correct tenant names"""

import requests
import sqlite3
from datetime import date, datetime
from pathlib import Path

PROD_API = "https://inmuebles-backend-api.onrender.com"
LOCAL_API = "http://localhost:8000"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

# Extract tenant names and property addresses from filenames
CONTRACT_DATA = {
    "contract_1": {"tenant": "Rocío", "address": "Aranguren, 68", "date": "2022-11-18"},
    "contract_2": {"tenant": "Susana y Jorge", "address": "Aranguren, 66", "date": "2022-06-30"},
    "contract_3": {"tenant": "Álvaro", "address": "Aranguren, 22", "date": "2025-06-14"},
    "contract_4": {"tenant": "J. Antonio y María", "address": "Aranguren, 22", "date": "2023-12-16"},
    "contract_5": {"tenant": "Álvaro", "address": "Aranguren, 22", "date": "2025-06-14"},
    "contract_6": {"tenant": "Antonio y Olga", "address": "Platón, 30", "date": "2024-01-01"},
    "contract_7": {"tenant": "Diego y Soledad", "address": "Platón, 30", "date": "2022-07-01"},
    "contract_8": {"tenant": "Leandro Emanuel", "address": "Pozoalbero", "date": "2025-02-24"},
    "contract_9": {"tenant": "Sergio Bravo Bañasco", "address": "Pozoalbero", "date": "2024-02-25"},
    "contract_10": {"tenant": "Judit y Jesús", "address": "Lago de Enol, 1. P. 1-1F", "date": "2025-01-12"},
    "contract_11": {"tenant": "Antonio", "address": "Lago de Enol, P. 1. Planta 2. Letra A", "date": "2023-06-11"},
    "contract_12": {"tenant": "Inquilino", "address": "Propiedad", "date": "2024-01-01"},
    "contract_14": {"tenant": "Roberto y Kerthyns", "address": "Lago de Enol, 1. Bloque 2. Bajo n.4", "date": "2025-01-17"},
    "contract_15": {"tenant": "Manuela", "address": "Lago de Enol, Bloque 2. Bajo 4", "date": "2023-06-15"},
    "contract_16": {"tenant": "Judit", "address": "Lago de Enol. Bloque 2. Bajo n. 4", "date": "2024-10-22"},
    "contract_17": {"tenant": "Jesús Javier y Carolina Olalla", "address": "Lago de Enol. Bloque 2. 1 P. Vivienda nº 9", "date": "2023-07-29"},
    "contract_18": {"tenant": "Lucía", "address": "Lago de Enol, 2. 2ª planta. Número 9", "date": "2025-05-02"},
    "contract_19": {"tenant": "Manuel Orellana", "address": "Lago de Enol, 1. P1. 1ºG", "date": "2024-08-27"},
    "contract_20": {"tenant": "Eva y Manuel", "address": "Lago de Enol. 1-1G", "date": "2025-07-01"}
}

def login(api_url):
    try:
        response = requests.post(f"{api_url}/auth/login", 
                               data={"username": EMAIL, "password": PASSWORD}, timeout=10)
        return response.json()["access_token"] if response.status_code == 200 else None
    except:
        return None

def get_property_mapping(token):
    """Get properties from production to map addresses to IDs"""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{PROD_API}/properties", headers=headers, timeout=10)
        if response.status_code == 200:
            properties = response.json()
            # Create mapping of address parts to property IDs
            mapping = {}
            for prop in properties:
                addr = prop['address'].lower()
                prop_id = prop['id']
                
                # Map by key parts of address
                if "aranguren 68" in addr or "aranguren, 68" in addr:
                    mapping["Aranguren, 68"] = prop_id
                elif "aranguren 66" in addr or "aranguren, 66" in addr:
                    mapping["Aranguren, 66"] = prop_id
                elif "aranguren 22" in addr or "aranguren, 22" in addr:
                    mapping["Aranguren, 22"] = prop_id
                elif "platon" in addr or "platón" in addr:
                    mapping["Platón, 30"] = prop_id
                elif "pozoalbero" in addr or "seneca" in addr:
                    mapping["Pozoalbero"] = prop_id
                elif "lago de enol" in addr:
                    if "1-1f" in addr.lower() or "p. 1-1f" in addr.lower():
                        mapping["Lago de Enol, 1. P. 1-1F"] = prop_id
                    elif "planta 2. letra a" in addr.lower() or "planta segunda, puerta a" in addr.lower():
                        mapping["Lago de Enol, P. 1. Planta 2. Letra A"] = prop_id
                    elif "bloque 2. bajo" in addr.lower() or "bajo n.4" in addr.lower() or "bajo 4" in addr.lower():
                        mapping["Lago de Enol, Bloque 2. Bajo 4"] = prop_id
                        mapping["Lago de Enol, 1. Bloque 2. Bajo n.4"] = prop_id
                        mapping["Lago de Enol. Bloque 2. Bajo n. 4"] = prop_id
                    elif "vivienda nº 9" in addr.lower() or "número 9" in addr.lower() or "puerta 9" in addr.lower():
                        mapping["Lago de Enol. Bloque 2. 1 P. Vivienda nº 9"] = prop_id
                        mapping["Lago de Enol, 2. 2ª planta. Número 9"] = prop_id
                    elif "1ºg" in addr.lower() or "1-1g" in addr.lower() or "puerta g" in addr.lower():
                        mapping["Lago de Enol, 1. P1. 1ºG"] = prop_id
                        mapping["Lago de Enol. 1-1G"] = prop_id
                    
            return mapping
    except Exception as e:
        print(f"Error getting properties: {e}")
    return {}

def upload_contracts():
    print("UPLOADING ALL RENTAL CONTRACTS")
    print("=" * 40)
    
    # Login to production
    prod_token = login(PROD_API)
    if not prod_token:
        print("Production login failed!")
        return
    
    print("Login successful!")
    headers = {"Authorization": f"Bearer {prod_token}"}
    
    # Get property mapping
    prop_mapping = get_property_mapping(prod_token)
    print(f"\nProperty mapping found: {len(prop_mapping)} mappings")
    
    # Get existing contracts to avoid duplicates
    try:
        response = requests.get(f"{PROD_API}/rental-contracts/", headers=headers, timeout=10)
        existing_contracts = response.json() if response.status_code == 200 else []
        existing_tenants = {c['tenant_name'].lower() for c in existing_contracts}
        print(f"Existing contracts: {len(existing_contracts)}")
    except:
        existing_contracts = []
        existing_tenants = set()
    
    # Upload each contract
    uploaded = 0
    skipped = 0
    failed = 0
    
    for contract_key, contract_info in CONTRACT_DATA.items():
        tenant_name = contract_info["tenant"]
        address_key = contract_info["address"]
        start_date = contract_info["date"]
        
        # Skip if already exists
        if tenant_name.lower() in existing_tenants:
            print(f"Skipping {tenant_name} - already exists")
            skipped += 1
            continue
        
        # Find property ID
        property_id = None
        for key, pid in prop_mapping.items():
            if key in address_key or address_key in key:
                property_id = pid
                break
        
        if not property_id:
            # Try to find by partial match
            for key, pid in prop_mapping.items():
                if any(part in key.lower() for part in address_key.lower().split(",")):
                    property_id = pid
                    break
        
        if not property_id:
            print(f"WARNING: No property found for {address_key} - {tenant_name}")
            failed += 1
            continue
        
        # Create contract data
        contract_data = {
            "property_id": property_id,
            "tenant_name": tenant_name,
            "start_date": start_date,
            "end_date": None,  # Active contracts
            "monthly_rent": 650.0,  # Default rent
            "deposit": 1300.0,  # Default deposit (2 months)
            "is_active": True
        }
        
        # Upload contract
        try:
            response = requests.post(f"{PROD_API}/rental-contracts/", 
                                   json=contract_data, 
                                   headers={**headers, "Content-Type": "application/json"},
                                   timeout=15)
            
            if response.status_code in [200, 201]:
                uploaded += 1
                print(f"✓ Uploaded: {tenant_name} -> Property ID {property_id}")
            else:
                failed += 1
                print(f"✗ Failed: {tenant_name} - {response.status_code}")
                if response.status_code == 422:
                    print(f"  Error: {response.json()}")
                    
        except Exception as e:
            failed += 1
            print(f"✗ Error uploading {tenant_name}: {str(e)[:50]}")
    
    print(f"\n" + "=" * 40)
    print(f"SUMMARY:")
    print(f"  Uploaded: {uploaded}")
    print(f"  Skipped (already exist): {skipped}")
    print(f"  Failed: {failed}")
    
    # Final check
    try:
        response = requests.get(f"{PROD_API}/rental-contracts/", headers=headers, timeout=10)
        if response.status_code == 200:
            final_contracts = response.json()
            print(f"\nFinal total contracts: {len(final_contracts)}")
            print("\nTenant names in system:")
            for contract in final_contracts:
                print(f"  - {contract['tenant_name']}")
    except:
        print("Could not verify final state")

if __name__ == "__main__":
    upload_contracts()