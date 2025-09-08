#!/usr/bin/env python3
"""Upload contracts when production is ready"""

import requests
import time
from pathlib import Path

BACKEND_URL = "https://inmuebles-backend-api.onrender.com"
USER_EMAIL = "davsanchez21277@gmail.com"
USER_PASSWORD = "123456"

def wait_for_deployment():
    """Wait for deployment to be ready"""
    print("Waiting for deployment to be ready...")
    
    for i in range(30):  # Wait up to 5 minutes
        try:
            # Test health endpoint
            response = requests.get(f"{BACKEND_URL}/health", timeout=10)
            if response.status_code == 200:
                
                # Test login
                login_data = {"username": USER_EMAIL, "password": USER_PASSWORD}
                login_resp = requests.post(
                    f"{BACKEND_URL}/auth/login",
                    data=login_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=10
                )
                
                if login_resp.status_code == 200:
                    token = login_resp.json()["access_token"]
                    headers = {"Authorization": f"Bearer {token}"}
                    
                    # Test uploads endpoint
                    uploads_resp = requests.get(f"{BACKEND_URL}/uploads/", headers=headers, timeout=10)
                    
                    if uploads_resp.status_code != 404:  # Not 404 means endpoint exists
                        print("✅ Deployment is ready!")
                        return token
                        
        except:
            pass
            
        print(f"⏳ Checking... ({i+1}/30)")
        time.sleep(10)
    
    print("❌ Deployment not ready after 5 minutes")
    return None

def upload_all_contracts(token):
    """Upload all contracts"""
    headers = {"Authorization": f"Bearer {token}"}
    contracts_dir = Path("data/assets/contracts")
    
    contracts = list(contracts_dir.glob("*.pdf")) + list(contracts_dir.glob("*.PDF"))
    print(f"Found {len(contracts)} contracts to upload")
    
    uploaded = 0
    for i, contract in enumerate(contracts, 1):
        try:
            print(f"Uploading {i}/{len(contracts)}")
            
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
                    print(f"  ✅ Success")
                else:
                    print(f"  ❌ Failed: {response.status_code}")
                    
        except Exception as e:
            print(f"  ❌ Error")
        
        time.sleep(1)
    
    print(f"\n🎉 Upload complete: {uploaded}/{len(contracts)} contracts")
    return uploaded

def main():
    print("🚀 Waiting for deployment and uploading contracts...")
    
    token = wait_for_deployment()
    if token:
        uploaded = upload_all_contracts(token)
        print(f"\n✅ ALL DONE! {uploaded} contracts uploaded successfully!")
        
        # Test photo URL
        photo_resp = requests.get("https://inmuebles-backend-api.onrender.com/uploads/photo/2282669a-f638-4dbd-832a-df2bb77509a4.jpg")
        print(f"📸 Photo test: {photo_resp.status_code} ({'✅ Working' if photo_resp.status_code == 200 else '❌ Still not working'})")
    else:
        print("❌ Could not complete - deployment not ready")

if __name__ == "__main__":
    main()