#!/usr/bin/env python3
"""Upload contracts in batches"""

import requests
import time
from pathlib import Path

PROD_API = "https://inmuebles-backend-api.onrender.com"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

def login():
    response = requests.post(f"{PROD_API}/auth/login", 
                           data={"username": EMAIL, "password": PASSWORD}, timeout=10)
    return response.json()["access_token"] if response.status_code == 200 else None

def upload_contracts_simple():
    token = login()
    if not token:
        return 0
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Find contracts
    contracts_dir = Path("inmuebles-backend/data/assets/contracts")
    if not contracts_dir.exists():
        contracts_dir = Path("data/assets/contracts")
    
    contracts = list(contracts_dir.glob("*.pdf"))
    print(f"Found {len(contracts)} contracts")
    
    uploaded = 0
    for i, contract_file in enumerate(contracts[:10]):  # Upload first 10
        try:
            simple_name = f"contract_{i+1:02d}.pdf"
            print(f"Uploading {simple_name}...")
            
            with open(contract_file, 'rb') as f:
                files = {'file': (simple_name, f, 'application/pdf')}
                response = requests.post(f"{PROD_API}/uploads/document", 
                                       files=files, headers=headers, timeout=30)
                
                if response.status_code in [200, 201]:
                    uploaded += 1
                    print(f"  OK")
                else:
                    print(f"  FAIL: {response.status_code}")
                    
        except Exception as e:
            print(f"  ERROR: {str(e)[:30]}")
        
        time.sleep(3)  # Longer pause
    
    return uploaded

if __name__ == "__main__":
    print("SIMPLE CONTRACT UPLOAD")
    print("=" * 30)
    uploaded = upload_contracts_simple()
    print(f"\nUploaded: {uploaded} contracts")