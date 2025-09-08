#!/usr/bin/env python3
"""Fix final contract issues"""

import requests

PROD_API = "https://inmuebles-backend-api.onrender.com"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

def fix_contracts():
    print("FIXING FINAL CONTRACT ISSUES")
    print("=" * 30)
    
    # Login
    response = requests.post(f"{PROD_API}/auth/login", 
                           data={"username": EMAIL, "password": PASSWORD}, timeout=10)
    if response.status_code != 200:
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get contracts
    response = requests.get(f"{PROD_API}/rental-contracts/", headers=headers, timeout=10)
    contracts = response.json()
    
    # Find and delete duplicate Rocio
    rocio_contracts = [c for c in contracts if "Roc" in c['tenant_name']]
    if len(rocio_contracts) > 1:
        print(f"Found {len(rocio_contracts)} Rocio contracts:")
        for c in rocio_contracts:
            print(f"  - {c['tenant_name']} (ID: {c['id']})")
        
        # Keep only one (prefer simple "Rocio")
        to_delete = [c for c in rocio_contracts if c['tenant_name'] != "Rocio"][0]
        print(f"Deleting: {to_delete['tenant_name']} (ID: {to_delete['id']})")
        
        response = requests.delete(f"{PROD_API}/rental-contracts/{to_delete['id']}", 
                                 headers=headers, timeout=10)
        if response.status_code in [200, 204]:
            print("Deleted successfully")
    
    # Final summary
    response = requests.get(f"{PROD_API}/rental-contracts/", headers=headers, timeout=10)
    final = response.json()
    
    print(f"\nFINAL CONTRACTS: {len(final)}")
    print("\nAll tenant names:")
    
    # Get properties for better display
    response = requests.get(f"{PROD_API}/properties", headers=headers, timeout=10)
    properties = {p['id']: p['address'] for p in response.json()}
    
    # Sort by property
    by_prop = {}
    for c in final:
        prop_id = c['property_id']
        if prop_id not in by_prop:
            by_prop[prop_id] = []
        by_prop[prop_id].append(c['tenant_name'])
    
    for prop_id, tenants in sorted(by_prop.items()):
        addr = properties.get(prop_id, f"Property {prop_id}")
        # Shorten address
        if "Jose Luis Lopez de Aranguren" in addr:
            addr = addr.replace("Jose Luis Lopez de Aranguren", "Aranguren")
        if "Lago de Enol" in addr:
            addr = "Lago de Enol"
        if "Seneca" in addr:
            addr = "Pozoalbero"
        
        print(f"\n{addr}:")
        for tenant in tenants:
            print(f"  - {tenant}")
    
    print(f"\n" + "=" * 30)
    print(f"TOTAL: {len(final)} contracts")

if __name__ == "__main__":
    fix_contracts()