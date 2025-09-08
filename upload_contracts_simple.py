#!/usr/bin/env python3
"""Simple contract upload script"""

import requests
from pathlib import Path
import time

BACKEND_URL = "https://inmuebles-backend-api.onrender.com"
USER_EMAIL = "davsanchez21277@gmail.com"
USER_PASSWORD = "123456"

def main():
    print("Testing deployment and uploading contracts...")
    
    try:
        # Test photo URL first
        photo_resp = requests.get(f"{BACKEND_URL}/uploads/photo/2282669a-f638-4dbd-832a-df2bb77509a4.jpg", timeout=10)
        print(f"Photo test: {photo_resp.status_code}")
        
        if photo_resp.status_code == 200:
            print("PHOTOS ARE WORKING!")
        
        # Login
        login_data = {"username": USER_EMAIL, "password": USER_PASSWORD}
        login_resp = requests.post(
            f"{BACKEND_URL}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        if login_resp.status_code != 200:
            print(f"Login failed: {login_resp.status_code}")
            return
        
        print("Login successful")
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Find and upload contracts
        contracts_dir = Path("data/assets/contracts")
        contracts = list(contracts_dir.glob("*.pdf")) + list(contracts_dir.glob("*.PDF"))
        print(f"Found {len(contracts)} contracts")
        
        uploaded = 0
        failed = 0
        
        for i, contract in enumerate(contracts[:5], 1):  # Upload first 5 as test
            try:
                print(f"Uploading {i}/5: {contract.name[:50]}...")
                
                with open(contract, 'rb') as f:
                    files = {'file': (contract.name, f, 'application/pdf')}
                    response = requests.post(
                        f"{BACKEND_URL}/uploads/document",
                        files=files,
                        headers=headers,
                        timeout=30
                    )
                    
                    if response.status_code in [200, 201]:
                        uploaded += 1
                        print(f"  SUCCESS")
                    else:
                        failed += 1
                        print(f"  FAILED: {response.status_code}")
                        
            except Exception as e:
                failed += 1
                print(f"  ERROR")
            
            time.sleep(1)
        
        print(f"\nTest upload complete: {uploaded} success, {failed} failed")
        
        if uploaded > 0:
            print("Contract uploads are working! Ready to upload all 38 contracts.")
        
    except Exception as e:
        print(f"Connection error: {type(e).__name__}")

if __name__ == "__main__":
    main()