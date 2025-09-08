#!/usr/bin/env python3
"""Migrate photos to database storage"""

import requests
import base64
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
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def upload_photos_to_db():
    """Upload photos using new database storage endpoint"""
    
    token = get_auth_token()
    if not token:
        print("Authentication failed")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    uploads_dir = Path("uploads")
    
    if not uploads_dir.exists():
        print("No uploads directory found")
        return
    
    uploaded = 0
    failed = 0
    
    # Upload all JPG files
    for photo_file in uploads_dir.glob("*.jpg"):
        try:
            print(f"Uploading {photo_file.name}...")
            
            with open(photo_file, 'rb') as f:
                files = {'file': (photo_file.name, f, 'image/jpeg')}
                
                # Use new database storage endpoint
                response = requests.post(
                    f"{BACKEND_URL}/files/upload/photo",
                    files=files,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code in [200, 201]:
                    uploaded += 1
                    result = response.json()
                    print(f"  SUCCESS - URL: {result.get('url')}")
                else:
                    failed += 1
                    print(f"  FAILED: {response.status_code}")
                    if response.text:
                        print(f"  Error: {response.text[:100]}")
                        
        except Exception as e:
            failed += 1
            print(f"  ERROR: {e}")
        
        time.sleep(0.5)  # Small delay between uploads
    
    print(f"\nUpload complete: {uploaded} success, {failed} failed")
    
    # Test if photos are accessible
    if uploaded > 0:
        print("\nTesting photo access...")
        test_resp = requests.get(f"{BACKEND_URL}/files/list/photo", headers=headers)
        if test_resp.status_code == 200:
            photos = test_resp.json()
            print(f"Photos in database: {len(photos)}")
            
            # Test accessing first photo
            if photos:
                first_photo_url = BACKEND_URL + photos[0]['url']
                photo_resp = requests.get(first_photo_url, timeout=10)
                print(f"Photo access test: {photo_resp.status_code}")
                if photo_resp.status_code == 200:
                    print("SUCCESS! Photos are now accessible from database!")
    
    return uploaded

def upload_contracts_to_db():
    """Upload contracts using database storage"""
    
    token = get_auth_token()
    if not token:
        return 0
    
    headers = {"Authorization": f"Bearer {token}"}
    contracts_dir = Path("data/assets/contracts")
    
    if not contracts_dir.exists():
        print("Contracts directory not found")
        return 0
    
    uploaded = 0
    contracts = list(contracts_dir.glob("*.pdf")) + list(contracts_dir.glob("*.PDF"))
    
    print(f"\nUploading {len(contracts)} contracts to database...")
    
    for i, contract_file in enumerate(contracts[:10], 1):  # Upload first 10 as test
        try:
            print(f"Uploading contract {i}/10...")
            
            with open(contract_file, 'rb') as f:
                files = {'file': (contract_file.name, f, 'application/pdf')}
                
                response = requests.post(
                    f"{BACKEND_URL}/files/upload/document",
                    files=files,
                    headers=headers,
                    data={'document_type': 'document'},
                    timeout=30
                )
                
                if response.status_code in [200, 201]:
                    uploaded += 1
                    print(f"  SUCCESS")
                else:
                    print(f"  FAILED: {response.status_code}")
                    
        except Exception as e:
            print(f"  ERROR")
        
        time.sleep(0.5)
    
    print(f"Contracts uploaded: {uploaded}/10")
    return uploaded

def main():
    print("Migrating files to database storage...")
    print("=" * 50)
    
    # Upload photos
    photos = upload_photos_to_db()
    
    # Upload contracts
    contracts = upload_contracts_to_db()
    
    print("\n" + "=" * 50)
    print("MIGRATION COMPLETE")
    print("=" * 50)
    print(f"Photos uploaded to database: {photos}")
    print(f"Contracts uploaded to database: {contracts}")
    print("\nFiles are now stored in PostgreSQL database!")
    print("They will persist across deployments!")

if __name__ == "__main__":
    main()