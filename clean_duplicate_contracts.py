#!/usr/bin/env python3
"""Clean duplicate contracts and ensure correct data"""

import requests

PROD_API = "https://inmuebles-backend-api.onrender.com"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

def clean_duplicates():
    print("CLEANING DUPLICATE CONTRACTS")
    print("=" * 30)
    
    # Login
    response = requests.post(f"{PROD_API}/auth/login", 
                           data={"username": EMAIL, "password": PASSWORD}, timeout=10)
    if response.status_code != 200:
        print(f"Login failed")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login OK")
    
    # Get all contracts
    response = requests.get(f"{PROD_API}/rental-contracts/", headers=headers, timeout=10)
    if response.status_code != 200:
        print("Failed to get contracts")
        return
    
    contracts = response.json()
    print(f"Total contracts: {len(contracts)}")
    
    # Group by property to check for duplicates
    by_property = {}
    for contract in contracts:
        prop_id = contract['property_id']
        if prop_id not in by_property:
            by_property[prop_id] = []
        by_property[prop_id].append(contract)
    
    # Check for duplicates
    duplicates_found = False
    for prop_id, prop_contracts in by_property.items():
        if len(prop_contracts) > 1:
            print(f"\nProperty {prop_id} has {len(prop_contracts)} contracts:")
            for c in prop_contracts:
                print(f"  - {c['tenant_name']} (ID: {c['id']}, Active: {c.get('is_active', True)})")
            
            # Keep only the most recent or with better name
            if any("Rocio Soto" in c['tenant_name'] or "Roc" in c['tenant_name'] for c in prop_contracts):
                duplicates_found = True
                # Find the best Rocio entry
                rocio_contracts = [c for c in prop_contracts if "Roc" in c['tenant_name']]
                if len(rocio_contracts) > 1:
                    # Keep "Rocio" (simple), delete others
                    for c in rocio_contracts:
                        if c['tenant_name'] not in ["Rocio", "Rocío"]:
                            print(f"    -> Deleting duplicate: {c['tenant_name']} (ID: {c['id']})")
                            try:
                                response = requests.delete(f"{PROD_API}/rental-contracts/{c['id']}", 
                                                         headers=headers, timeout=10)
                                if response.status_code in [200, 204]:
                                    print(f"       Deleted successfully")
                            except:
                                print(f"       Failed to delete")
    
    if not duplicates_found:
        print("\nNo problematic duplicates found")
    
    # Final check
    response = requests.get(f"{PROD_API}/rental-contracts/", headers=headers, timeout=10)
    if response.status_code == 200:
        final = response.json()
        print(f"\nFinal contracts: {len(final)}")
        
        # Group by property address for better view
        response = requests.get(f"{PROD_API}/properties", headers=headers, timeout=10)
        if response.status_code == 200:
            properties = {p['id']: p['address'] for p in response.json()}
            
            print("\nContracts by property:")
            for prop_id, prop_contracts in by_property.items():
                address = properties.get(prop_id, f"Property {prop_id}")
                print(f"\n{address}:")
                for c in prop_contracts:
                    if c['id'] in [contract['id'] for contract in final]:
                        print(f"  - {c['tenant_name']}")

if __name__ == "__main__":
    clean_duplicates()