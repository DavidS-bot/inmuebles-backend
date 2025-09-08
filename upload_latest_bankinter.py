#!/usr/bin/env python3
"""
Upload the latest Bankinter file to the system
"""

import glob
import os
import requests
from datetime import datetime

def upload_latest_bankinter():
    """Find and upload the latest Bankinter Excel file"""
    
    print("Finding latest Bankinter file...")
    
    # Find all bankinter files
    pattern = "bankinter_api_*.xlsx"
    files = glob.glob(pattern)
    
    if not files:
        print("No Bankinter files found")
        return
    
    # Sort by modification time, get the latest
    latest_file = max(files, key=os.path.getmtime)
    file_size = os.path.getsize(latest_file)
    mod_time = datetime.fromtimestamp(os.path.getmtime(latest_file))
    
    print(f"Latest file: {latest_file}")
    print(f"Size: {file_size} bytes")
    print(f"Modified: {mod_time}")
    
    # Login to backend
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    print("Logging into backend...")
    login_data = {'username': 'davsanchez21277@gmail.com', 'password': '123456'}
    
    try:
        response = requests.post(
            f'{backend_url}/auth/login',
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"Login failed: {response.status_code}")
            return
        
        token = response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        print("Login successful")
        
        # Upload the Excel file
        print(f"Uploading {latest_file}...")
        
        with open(latest_file, 'rb') as file:
            files = {'file': (latest_file, file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            response = requests.post(
                f'{backend_url}/financial-movements/upload-excel-global',
                files=files,
                headers=headers,
                timeout=60
            )
            
        print(f"Upload status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("SUCCESS! Upload completed:")
            print(f"  Movements created: {result.get('created_movements', 0)}")
            print(f"  Total rows processed: {result.get('total_rows', 0)}")
            print(f"  Duplicates skipped: {result.get('duplicates_skipped', 0)}")
            
            if result.get('errors'):
                print(f"  Errors: {len(result['errors'])}")
                for i, error in enumerate(result['errors'][:5]):
                    print(f"    {i+1}. {error}")
        else:
            print(f"Upload failed: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    upload_latest_bankinter()