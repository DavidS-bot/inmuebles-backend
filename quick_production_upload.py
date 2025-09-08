#!/usr/bin/env python3
"""Quick upload to fix production data"""

import requests
import json
from pathlib import Path

BACKEND_URL = "https://inmuebles-backend-api.onrender.com"
USER_EMAIL = "davsanchez21277@gmail.com"
USER_PASSWORD = "123456"

def get_auth_token():
    try:
        login_data = {"username": USER_EMAIL, "password": USER_PASSWORD}
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"Login failed with status: {response.status_code}")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def check_mortgage_data(token):
    """Check if mortgage data exists"""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{BACKEND_URL}/mortgage-details/", headers=headers, timeout=10)
        print(f"Mortgage data check: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} mortgage records")
            return data
        else:
            print("No mortgage data or access denied")
            return []
    except Exception as e:
        print(f"Error checking mortgages: {e}")
        return []

def upload_single_contract(token, contract_file):
    """Upload a single contract"""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        with open(contract_file, 'rb') as f:
            files = {'file': (contract_file.name, f, 'application/pdf')}
            response = requests.post(
                f"{BACKEND_URL}/uploads/document",
                files=files,
                headers=headers,
                timeout=30
            )
            return response.status_code in [200, 201]
    except Exception as e:
        print(f"Upload error: {e}")
        return False

def main():
    print("Quick Production Data Upload")
    print("=" * 40)
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("Cannot proceed without authentication")
        return
    
    print("✓ Authentication successful!")
    
    # Check mortgage data
    mortgages = check_mortgage_data(token)
    
    # Upload a few key contracts
    contracts_dir = Path("inmuebles-backend/data/assets/contracts")
    if contracts_dir.exists():
        contracts = list(contracts_dir.glob("*.pdf"))[:5]  # Upload first 5 only
        print(f"Uploading {len(contracts)} contracts...")
        
        uploaded = 0
        for contract in contracts:
            if upload_single_contract(token, contract):
                uploaded += 1
                print(f"✓ Uploaded {contract.name}")
            else:
                print(f"✗ Failed {contract.name}")
        
        print(f"Uploaded {uploaded}/{len(contracts)} contracts")
    else:
        print("Contracts directory not found")
    
    print("Quick upload completed!")

if __name__ == "__main__":
    main()