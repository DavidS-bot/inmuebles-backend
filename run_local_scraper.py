#!/usr/bin/env python3
"""
Run local Bankinter scraper and upload to production
"""

import os
import glob
import requests
from datetime import datetime
import subprocess
import sys

def run_local_scraper_and_upload():
    """Run local scraper and upload results"""
    
    print("Running local Bankinter scraper...")
    
    # First, let's try to run a simple scraper that works
    try:
        # Look for existing recent files first
        pattern = "bankinter_api_*.xlsx"
        files = glob.glob(pattern)
        
        if files:
            # Get the most recent file
            latest_file = max(files, key=os.path.getmtime)
            mod_time = datetime.fromtimestamp(os.path.getmtime(latest_file))
            
            # If the file is less than 1 hour old, use it
            if (datetime.now() - mod_time).seconds < 3600:
                print(f"Using recent file: {latest_file} (modified {mod_time})")
                return upload_file(latest_file)
        
        print("No recent files found, need to run scraper...")
        print("Trying to run bankinter_simple_working.py...")
        
        # Try to run the simple working scraper
        result = subprocess.run([sys.executable, 'bankinter_simple_working.py'], 
                              capture_output=True, 
                              text=True, 
                              timeout=300)  # 5 minute timeout
        
        if result.returncode == 0:
            print("Scraper completed successfully!")
            
            # Look for new files
            new_files = glob.glob(pattern)
            if new_files:
                latest_file = max(new_files, key=os.path.getmtime)
                return upload_file(latest_file)
        else:
            print(f"Scraper failed: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("Scraper timed out")
    except Exception as e:
        print(f"Error running scraper: {e}")
    
    return False

def upload_file(filepath):
    """Upload file to production backend"""
    
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    print(f"Uploading {filepath} to production...")
    
    try:
        # Login
        login_data = {'username': 'davsanchez21277@gmail.com', 'password': '123456'}
        response = requests.post(
            f'{backend_url}/auth/login',
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"Login failed: {response.status_code}")
            return False
        
        token = response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Upload file
        with open(filepath, 'rb') as file:
            files = {'file': (filepath, file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            response = requests.post(
                f'{backend_url}/financial-movements/upload-excel-global',
                files=files,
                headers=headers,
                timeout=60
            )
        
        if response.status_code == 200:
            result = response.json()
            
            print("Upload successful!")
            print(f"Created movements: {result.get('created_movements', 0)}")
            print(f"Total rows: {result.get('total_rows', 0)}")
            print(f"Duplicates skipped: {result.get('duplicates_skipped', 0)}")
            return True
        else:
            print(f"Upload failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Error uploading: {e}")
        return False

if __name__ == "__main__":
    success = run_local_scraper_and_upload()
    if success:
        print("SUCCESS: Local scraper ran and uploaded to production!")
    else:
        print("FAILED: Could not complete scraping and upload")