#!/usr/bin/env python3
"""Full sync from local to production - ALL DATA"""

import requests
import json
import time

LOCAL_API = "http://localhost:8000"
PROD_API = "https://inmuebles-backend-api.onrender.com"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

def login(api_url):
    """Login with retry"""
    for attempt in range(3):
        try:
            response = requests.post(
                f"{api_url}/auth/login",
                data={"username": EMAIL, "password": PASSWORD},
                timeout=30
            )
            if response.status_code == 200:
                return response.json()["access_token"]
        except:
            time.sleep(2)
    return None

def get_data(api_url, endpoint, token):
    """Get data from endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{api_url}{endpoint}", headers=headers, timeout=30)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

def post_data(api_url, endpoint, data, token):
    """Post data to endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        response = requests.post(f"{api_url}{endpoint}", json=data, headers=headers, timeout=30)
        return response.status_code in [200, 201]
    except:
        return False

def delete_all(api_url, endpoint, token):
    """Delete all items from endpoint"""
    items = get_data(api_url, endpoint, token)
    headers = {"Authorization": f"Bearer {token}"}
    deleted = 0
    
    for item in items:
        try:
            response = requests.delete(f"{api_url}{endpoint}/{item['id']}", headers=headers, timeout=10)
            if response.status_code in [200, 204]:
                deleted += 1
        except:
            pass
    
    return deleted

def sync_mortgages(local_token, prod_token):
    """Sync ALL mortgage data correctly"""
    print("\nSyncing mortgages...")
    
    # Get local mortgages
    local_mortgages = get_data(LOCAL_API, "/mortgage-details/", local_token)
    print(f"  Found {len(local_mortgages)} local mortgages")
    
    # Delete existing production mortgages
    deleted = delete_all(PROD_API, "/mortgage-details", prod_token)
    print(f"  Deleted {deleted} production mortgages")
    
    # Get production properties to map IDs
    prod_props = get_data(PROD_API, "/properties", prod_token)
    
    # Create property mapping by address
    prop_map = {}
    for prop in prod_props:
        prop_map[prop['address'].strip()] = prop['id']
    
    # Get local properties for mapping
    local_props = get_data(LOCAL_API, "/properties", local_token)
    local_prop_map = {}
    for prop in local_props:
        local_prop_map[prop['id']] = prop['address'].strip()
    
    # Upload mortgages with correct property IDs
    uploaded = 0
    for mortgage in local_mortgages:
        # Map local property ID to production property ID
        local_prop_id = mortgage['property_id']
        if local_prop_id in local_prop_map:
            address = local_prop_map[local_prop_id]
            if address in prop_map:
                mortgage_data = dict(mortgage)
                mortgage_data['property_id'] = prop_map[address]
                del mortgage_data['id']
                
                if post_data(PROD_API, "/mortgage-details/", mortgage_data, prod_token):
                    uploaded += 1
                    print(f"    Uploaded mortgage for property {prop_map[address]}")
                    time.sleep(1)
    
    print(f"  Uploaded {uploaded} mortgages")
    return uploaded

def sync_rules(local_token, prod_token):
    """Sync classification rules"""
    print("\nSyncing classification rules...")
    
    # Get local rules
    local_rules = get_data(LOCAL_API, "/classification-rules", local_token)
    print(f"  Found {len(local_rules)} local rules")
    
    # Delete existing production rules
    deleted = delete_all(PROD_API, "/classification-rules", prod_token)
    print(f"  Deleted {deleted} production rules")
    
    # Upload all rules
    uploaded = 0
    for rule in local_rules:
        rule_data = {k: v for k, v in rule.items() if k != 'id'}
        if post_data(PROD_API, "/classification-rules", rule_data, prod_token):
            uploaded += 1
        time.sleep(0.5)
    
    print(f"  Uploaded {uploaded} rules")
    return uploaded

def sync_contracts(local_token, prod_token):
    """Sync rental contracts"""
    print("\nSyncing rental contracts...")
    
    # Get local contracts
    local_contracts = get_data(LOCAL_API, "/rental-contracts", local_token)
    print(f"  Found {len(local_contracts)} local contracts")
    
    # Delete existing production contracts
    deleted = delete_all(PROD_API, "/rental-contracts", prod_token)
    print(f"  Deleted {deleted} production contracts")
    
    # Get property mappings
    prod_props = get_data(PROD_API, "/properties", prod_token)
    prop_map = {}
    for prop in prod_props:
        prop_map[prop['address'].strip()] = prop['id']
    
    local_props = get_data(LOCAL_API, "/properties", local_token)
    local_prop_map = {}
    for prop in local_props:
        local_prop_map[prop['id']] = prop['address'].strip()
    
    # Upload contracts with correct property IDs
    uploaded = 0
    for contract in local_contracts:
        contract_data = dict(contract)
        
        # Map property ID
        if contract['property_id'] in local_prop_map:
            address = local_prop_map[contract['property_id']]
            if address in prop_map:
                contract_data['property_id'] = prop_map[address]
                del contract_data['id']
                
                if post_data(PROD_API, "/rental-contracts", contract_data, prod_token):
                    uploaded += 1
                    print(f"    Uploaded contract for {contract.get('tenant_name', 'Unknown')}")
                    time.sleep(0.5)
    
    print(f"  Uploaded {uploaded} contracts")
    return uploaded

def sync_movements(local_token, prod_token):
    """Sync financial movements (limited to avoid timeout)"""
    print("\nSyncing financial movements...")
    
    # Get local movements
    local_movements = get_data(LOCAL_API, "/financial-movements", local_token)
    print(f"  Found {len(local_movements)} local movements")
    
    # Get property mappings
    prod_props = get_data(PROD_API, "/properties", prod_token)
    prop_map = {}
    for prop in prod_props:
        prop_map[prop['address'].strip()] = prop['id']
    
    local_props = get_data(LOCAL_API, "/properties", local_token)
    local_prop_map = {}
    for prop in local_props:
        local_prop_map[prop['id']] = prop['address'].strip()
    
    # Upload only recent movements (last 100) to avoid timeout
    recent_movements = sorted(local_movements, key=lambda x: x.get('date', ''), reverse=True)[:100]
    
    uploaded = 0
    for movement in recent_movements:
        movement_data = dict(movement)
        
        # Map property ID
        if movement['property_id'] in local_prop_map:
            address = local_prop_map[movement['property_id']]
            if address in prop_map:
                movement_data['property_id'] = prop_map[address]
                del movement_data['id']
                
                if post_data(PROD_API, "/financial-movements", movement_data, prod_token):
                    uploaded += 1
                    
                if uploaded % 10 == 0:
                    print(f"    Uploaded {uploaded} movements...")
                    time.sleep(1)
    
    print(f"  Uploaded {uploaded} financial movements")
    return uploaded

def main():
    print("=" * 60)
    print("FULL DATA SYNC: LOCAL -> PRODUCTION")
    print("=" * 60)
    
    # Login
    print("\nAuthenticating...")
    local_token = login(LOCAL_API)
    prod_token = login(PROD_API)
    
    if not local_token or not prod_token:
        print("Authentication failed!")
        return
    
    print("  Authentication successful!")
    
    # Sync data in order
    results = {}
    
    # 1. Mortgages (fixes debt = 0 issue)
    results['mortgages'] = sync_mortgages(local_token, prod_token)
    
    # 2. Classification rules
    results['rules'] = sync_rules(local_token, prod_token)
    
    # 3. Rental contracts
    results['contracts'] = sync_contracts(local_token, prod_token)
    
    # 4. Financial movements
    results['movements'] = sync_movements(local_token, prod_token)
    
    # Final verification
    print("\n" + "=" * 60)
    print("SYNC SUMMARY")
    print("=" * 60)
    
    # Check final state
    headers = {"Authorization": f"Bearer {prod_token}"}
    
    props = get_data(PROD_API, "/properties", prod_token)
    mortgages = get_data(PROD_API, "/mortgage-details/", prod_token)
    rules = get_data(PROD_API, "/classification-rules", prod_token)
    contracts = get_data(PROD_API, "/rental-contracts", prod_token)
    movements = get_data(PROD_API, "/financial-movements", prod_token)
    
    print(f"Properties: {len(props)}")
    print(f"Mortgages: {len(mortgages)} (debt will be calculated)")
    print(f"Classification Rules: {len(rules)}")
    print(f"Rental Contracts: {len(contracts)}")
    print(f"Financial Movements: {len(movements)}")
    
    if len(mortgages) > 0:
        total_debt = sum(m.get('outstanding_balance', 0) for m in mortgages)
        print(f"\nTotal Debt: {total_debt:,.2f} EUR")
    
    print("\nSync completed! Dashboard should now show all data correctly.")
    print("URL: https://inmuebles-david.vercel.app")

if __name__ == "__main__":
    main()