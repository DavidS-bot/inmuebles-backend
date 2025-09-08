#!/usr/bin/env python3
"""
Check what contracts exist in production
"""

import requests

PRODUCTION_URL = "https://inmuebles-backend-api.onrender.com"

def login_to_production() -> str:
    """Login and get token"""
    try:
        response = requests.post(
            f"{PRODUCTION_URL}/auth/login",
            data={
                'username': 'davsanchez21277@gmail.com',
                'password': '123456'
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('access_token')
        else:
            print(f"ERROR login: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"ERROR login: {e}")
        return None

def get_production_contracts(token: str):
    """Get all contracts from production"""
    try:
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.get(f"{PRODUCTION_URL}/rental-contracts/", headers=headers)
        
        if response.status_code == 200:
            contracts = response.json()
            print(f"Found {len(contracts)} contracts in production:")
            print()
            
            for contract in contracts:
                print(f"Contract ID: {contract.get('id')}")
                print(f"  Property ID: {contract.get('property_id')}")
                print(f"  Tenant: {contract.get('tenant_name')}")
                print(f"  PDF Path: {contract.get('contract_pdf_path')}")
                print(f"  PDF Name: {contract.get('contract_file_name')}")
                print(f"  Active: {contract.get('is_active')}")
                print()
                
            return contracts
        else:
            print(f"ERROR getting contracts: {response.status_code}")
            if response.text:
                print(f"Error details: {response.text}")
            return []
            
    except Exception as e:
        print(f"ERROR getting contracts: {e}")
        return []

def main():
    print("=== CHECK PRODUCTION CONTRACTS ===")
    print()
    
    # Login
    token = login_to_production()
    if not token:
        print("Cannot proceed without login")
        return
    
    print("Login successful!")
    print()
    
    # Get contracts
    contracts = get_production_contracts(token)
    
    if not contracts:
        print("No contracts found or error occurred")
    else:
        print(f"Summary: {len(contracts)} contracts found")

if __name__ == "__main__":
    main()