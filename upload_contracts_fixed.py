#!/usr/bin/env python3
"""Subir TODOS los contratos PDF"""

import os
import requests
from pathlib import Path
import time

BACKEND_URL = "https://inmuebles-backend-api.onrender.com"
USER_EMAIL = "davsanchez21277@gmail.com"
USER_PASSWORD = "123456"

def get_auth_token():
    login_data = {"username": USER_EMAIL, "password": USER_PASSWORD}
    response = requests.post(
        f"{BACKEND_URL}/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def main():
    print("Uploading all contracts...")
    
    token = get_auth_token()
    if not token:
        print("Auth failed")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    contracts_dir = Path("data/assets/contracts")
    
    if not contracts_dir.exists():
        print("Contracts directory not found")
        return
    
    uploaded = 0
    failed = 0
    
    all_contracts = list(contracts_dir.glob("*.pdf")) + list(contracts_dir.glob("*.PDF"))
    print(f"Found {len(all_contracts)} contract files")
    
    for i, contract_file in enumerate(all_contracts, 1):
        try:
            print(f"Uploading {i}/{len(all_contracts)}")
            
            with open(contract_file, 'rb') as f:
                files = {'file': (contract_file.name, f, 'application/pdf')}
                response = requests.post(
                    f"{BACKEND_URL}/uploads/document",
                    files=files,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code in [200, 201]:
                    uploaded += 1
                    print(f"  Success")
                else:
                    failed += 1
                    print(f"  Failed: {response.status_code}")
        except Exception as e:
            failed += 1
            print(f"  Error uploading file")
        
        time.sleep(0.5)
    
    print(f"\nSUMMARY:")
    print(f"Total files: {len(all_contracts)}")
    print(f"Uploaded: {uploaded}")
    print(f"Failed: {failed}")
    print("Done!")

if __name__ == "__main__":
    main()