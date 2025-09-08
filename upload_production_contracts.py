#!/usr/bin/env python3
"""Upload contracts to production backend"""

import requests
from pathlib import Path
import time
import sys

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

def test_upload_endpoint(token):
    """Test if upload endpoint exists"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test document endpoint
    try:
        response = requests.options(f"{BACKEND_URL}/uploads/document", headers=headers, timeout=5)
        print(f"Document endpoint status: {response.status_code}")
    except:
        print("Document endpoint not accessible")
    
    # Test if we can list uploaded files
    try:
        response = requests.get(f"{BACKEND_URL}/uploads/", headers=headers, timeout=5)
        print(f"Uploads list status: {response.status_code}")
    except:
        print("Cannot list uploads")

def upload_contracts_batch(token, contracts, batch_size=5):
    """Upload contracts in small batches"""
    headers = {"Authorization": f"Bearer {token}"}
    uploaded = 0
    failed = 0
    
    total = len(contracts)
    print(f"Starting upload of {total} contracts...")
    
    for i in range(0, total, batch_size):
        batch = contracts[i:i + batch_size]
        print(f"\nBatch {i//batch_size + 1}: Processing {len(batch)} files...")
        
        for j, contract_file in enumerate(batch):
            try:
                print(f"  {i+j+1}/{total}: Uploading...")
                
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
                        print(f"    SUCCESS")
                    else:
                        failed += 1
                        print(f"    FAILED: {response.status_code}")
                        if response.text:
                            print(f"    Error: {response.text[:100]}")
                            
            except Exception as e:
                failed += 1
                print(f"    ERROR: {str(e)[:100]}")
            
            time.sleep(1)  # Pause between uploads
        
        print(f"Batch complete. Uploaded: {uploaded}, Failed: {failed}")
        time.sleep(2)  # Pause between batches
    
    return uploaded, failed

def main():
    print("Production Contract Upload Tool")
    print("=" * 50)
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("Cannot proceed without authentication")
        return
    
    print("Authentication successful!")
    
    # Test endpoints
    test_upload_endpoint(token)
    
    # Find contracts
    contracts_dir = Path("data/assets/contracts")
    if not contracts_dir.exists():
        print(f"Contracts directory not found: {contracts_dir}")
        return
    
    contracts = list(contracts_dir.glob("*.pdf")) + list(contracts_dir.glob("*.PDF"))
    if not contracts:
        print("No contract files found")
        return
    
    print(f"Found {len(contracts)} contract files")
    
    # Upload in batches
    uploaded, failed = upload_contracts_batch(token, contracts)
    
    print("\n" + "=" * 50)
    print("UPLOAD SUMMARY")
    print("=" * 50)
    print(f"Total files: {len(contracts)}")
    print(f"Successfully uploaded: {uploaded}")
    print(f"Failed uploads: {failed}")
    
    if uploaded > 0:
        print(f"\n✓ {uploaded} contracts uploaded successfully!")
    if failed > 0:
        print(f"\n✗ {failed} contracts failed to upload")
    
    print("\nUpload process completed.")

if __name__ == "__main__":
    main()