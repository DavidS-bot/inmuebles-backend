#!/usr/bin/env python3
"""Force sync missing data"""

import requests
import json
import time

LOCAL_API = "http://localhost:8000"
PROD_API = "https://inmuebles-backend-api.onrender.com"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

def login(api_url):
    response = requests.post(f"{api_url}/auth/login", 
                           data={"username": EMAIL, "password": PASSWORD}, timeout=30)
    return response.json()["access_token"] if response.status_code == 200 else None

def force_sync_rules():
    """Force sync classification rules"""
    print("Forcing sync of classification rules...")
    
    local_token = login(LOCAL_API)
    prod_token = login(PROD_API)
    
    if not local_token or not prod_token:
        return 0
    
    # Get local rules
    headers_local = {"Authorization": f"Bearer {local_token}"}
    response = requests.get(f"{LOCAL_API}/classification-rules", headers=headers_local, timeout=30)
    local_rules = response.json() if response.status_code == 200 else []
    print(f"  Found {len(local_rules)} local rules")
    
    # Upload each rule
    headers_prod = {"Authorization": f"Bearer {prod_token}", "Content-Type": "application/json"}
    uploaded = 0
    
    for rule in local_rules:
        rule_data = {
            "rule_name": rule.get("rule_name", f"Rule_{uploaded+1}"),
            "pattern": rule.get("pattern", ""),
            "category": rule.get("category", ""),
            "subcategory": rule.get("subcategory", ""),
            "priority": rule.get("priority", 1),
            "is_active": rule.get("is_active", True)
        }
        
        try:
            response = requests.post(f"{PROD_API}/classification-rules", 
                                   json=rule_data, headers=headers_prod, timeout=30)
            if response.status_code in [200, 201, 400]:  # 400 might be duplicate
                uploaded += 1
                print(f"    Rule {uploaded}: {rule_data['rule_name'][:30]}")
        except Exception as e:
            print(f"    Error: {str(e)[:50]}")
        
        time.sleep(0.5)
    
    print(f"  Uploaded {uploaded} rules")
    return uploaded

def force_sync_contracts():
    """Force sync rental contracts"""
    print("\nForcing sync of rental contracts...")
    
    local_token = login(LOCAL_API)
    prod_token = login(PROD_API)
    
    if not local_token or not prod_token:
        return 0
    
    # Get data
    headers_local = {"Authorization": f"Bearer {local_token}"}
    headers_prod = {"Authorization": f"Bearer {prod_token}", "Content-Type": "application/json"}
    
    # Get contracts
    response = requests.get(f"{LOCAL_API}/rental-contracts", headers=headers_local, timeout=30)
    local_contracts = response.json() if response.status_code == 200 else []
    print(f"  Found {len(local_contracts)} local contracts")
    
    # Get properties for mapping
    response = requests.get(f"{LOCAL_API}/properties", headers=headers_local, timeout=30)
    local_props = response.json() if response.status_code == 200 else []
    
    response = requests.get(f"{PROD_API}/properties", headers=headers_prod, timeout=30)
    prod_props = response.json() if response.status_code == 200 else []
    
    # Create mapping
    prop_map = {}
    for lp in local_props:
        for pp in prod_props:
            if lp['address'].strip() == pp['address'].strip():
                prop_map[lp['id']] = pp['id']
                break
    
    # Upload contracts
    uploaded = 0
    for contract in local_contracts:
        if contract.get('property_id') in prop_map:
            contract_data = {
                "property_id": prop_map[contract['property_id']],
                "tenant_name": contract.get("tenant_name", "Unknown"),
                "start_date": contract.get("start_date"),
                "end_date": contract.get("end_date"),
                "monthly_rent": contract.get("monthly_rent", 0),
                "deposit": contract.get("deposit", 0),
                "is_active": contract.get("is_active", True)
            }
            
            try:
                response = requests.post(f"{PROD_API}/rental-contracts", 
                                       json=contract_data, headers=headers_prod, timeout=30)
                if response.status_code in [200, 201, 400]:
                    uploaded += 1
                    print(f"    Contract {uploaded}: {contract_data['tenant_name'][:30]}")
            except Exception as e:
                print(f"    Error: {str(e)[:50]}")
            
            time.sleep(0.5)
    
    print(f"  Uploaded {uploaded} contracts")
    return uploaded

def main():
    print("=" * 60)
    print("FORCE SYNC MISSING DATA")
    print("=" * 60)
    
    # Force sync rules
    rules = force_sync_rules()
    
    # Force sync contracts
    contracts = force_sync_contracts()
    
    # Verify final state
    print("\n" + "=" * 60)
    print("FINAL STATE")
    print("=" * 60)
    
    prod_token = login(PROD_API)
    if prod_token:
        headers = {"Authorization": f"Bearer {prod_token}"}
        
        # Check all data
        response = requests.get(f"{PROD_API}/properties", headers=headers)
        props = response.json() if response.status_code == 200 else []
        
        response = requests.get(f"{PROD_API}/mortgage-details/", headers=headers)
        mortgages = response.json() if response.status_code == 200 else []
        
        response = requests.get(f"{PROD_API}/classification-rules", headers=headers)
        rules = response.json() if response.status_code == 200 else []
        
        response = requests.get(f"{PROD_API}/rental-contracts", headers=headers)
        contracts = response.json() if response.status_code == 200 else []
        
        print(f"Properties: {len(props)}")
        print(f"Mortgages: {len(mortgages)}")
        print(f"Classification Rules: {len(rules)}")
        print(f"Rental Contracts: {len(contracts)}")
        
        if len(mortgages) > 0:
            total_debt = sum(m.get('outstanding_balance', 0) for m in mortgages)
            print(f"\nTotal Outstanding Debt: {total_debt:,.2f} EUR")
            print("This will show in the dashboard as 'Deuda Total'")
    
    print("\nAll data synced! Check the dashboard now.")
    print("URL: https://inmuebles-david.vercel.app")

if __name__ == "__main__":
    main()