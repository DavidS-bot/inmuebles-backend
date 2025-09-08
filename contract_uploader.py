#!/usr/bin/env python3
"""Upload all contract PDFs to production"""

import requests
import time
from pathlib import Path

PROD_API = "https://inmuebles-backend-api.onrender.com"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

def login():
    try:
        response = requests.post(
            f"{PROD_API}/auth/login",
            data={"username": EMAIL, "password": PASSWORD},
            timeout=10
        )
        return response.json()["access_token"] if response.status_code == 200 else None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def upload_contracts(token):
    """Upload all contract PDFs"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Find contracts directory
    contracts_dir = Path("inmuebles-backend/data/assets/contracts")
    if not contracts_dir.exists():
        contracts_dir = Path("data/assets/contracts") 
    
    if not contracts_dir.exists():
        print("Contracts directory not found!")
        return 0
    
    # Get all PDF files
    contracts = list(contracts_dir.glob("*.pdf")) + list(contracts_dir.glob("*.PDF"))
    print(f"Found {len(contracts)} contract files")
    
    uploaded = 0
    for contract_file in contracts:
        try:
            print(f"Uploading: {contract_file.name}")
            
            with open(contract_file, 'rb') as f:
                files = {'file': (contract_file.name, f, 'application/pdf')}
                response = requests.post(
                    f"{PROD_API}/uploads/document",
                    files=files,
                    headers=headers,
                    timeout=60
                )
                
                if response.status_code in [200, 201]:
                    uploaded += 1
                    print(f"  SUCCESS: {contract_file.name}")
                else:
                    print(f"  FAILED: {contract_file.name} - {response.status_code}")
                    
        except Exception as e:
            print(f"  ERROR: {contract_file.name} - {str(e)[:50]}")
        
        time.sleep(2)  # Avoid rate limiting
    
    return uploaded

def main():
    print("UPLOADING ALL CONTRACTS TO PRODUCTION")
    print("=" * 45)
    
    token = login()
    if not token:
        print("Login failed")
        return
    
    print("Login successful!")
    
    uploaded = upload_contracts(token)
    
    print("\n" + "=" * 45)
    print("CONTRACT UPLOAD SUMMARY")
    print("=" * 45)
    print(f"Successfully uploaded: {uploaded} contracts")
    print("\nAll contract PDFs should now be available in production!")

if __name__ == "__main__":
    main()