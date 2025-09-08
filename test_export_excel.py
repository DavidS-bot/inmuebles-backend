#!/usr/bin/env python3
"""Test Excel export functionality"""

import requests
import os

def test_excel_export():
    """Test the Excel export endpoint"""
    base_url = "http://localhost:8000"
    
    # Login first
    login_data = {
        "username": "davsanchez21277@gmail.com",
        "password": "123456"
    }
    
    response = requests.post(
        f"{base_url}/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("=== Testing Excel Export ===")
    
    # Test basic export (all movements)
    print("1. Testing basic export (all movements)...")
    export_url = f"{base_url}/financial-movements/download-xlsx"
    
    try:
        response = requests.get(export_url, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("[SUCCESS] Export endpoint is working!")
            
            # Check content type
            content_type = response.headers.get('content-type', '')
            print(f"Content-Type: {content_type}")
            
            # Check Content-Disposition header for filename
            content_disposition = response.headers.get('content-disposition', '')
            print(f"Content-Disposition: {content_disposition}")
            
            # Check file size
            content_length = len(response.content)
            print(f"File size: {content_length} bytes")
            
            if content_length > 1000:  # Should be a substantial Excel file
                # Save file for inspection
                test_filename = "test_export.xlsx"
                with open(test_filename, 'wb') as f:
                    f.write(response.content)
                print(f"[OK] Excel file saved as {test_filename} for inspection")
                
                # Try to read it back with pandas to verify it's a valid Excel file
                try:
                    import pandas as pd
                    df = pd.read_excel(test_filename)
                    print(f"[OK] Excel file is valid - Contains {len(df)} rows and {len(df.columns)} columns")
                    print(f"Columns: {list(df.columns)}")
                    
                    # Show first few rows
                    print("First 3 rows:")
                    for i, row in df.head(3).iterrows():
                        print(f"  Row {i+1}: {dict(row)}")
                    
                    # Clean up test file
                    os.remove(test_filename)
                    print(f"[OK] Test file cleaned up")
                    
                except Exception as e:
                    print(f"[ERROR] Could not read Excel file: {e}")
            else:
                print("[WARNING] File seems too small to be a valid Excel export")
        
        elif response.status_code == 404:
            print("[INFO] No movements found - this is expected if database is empty")
        else:
            print(f"[ERROR] Export failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
    
    # Test export with filters
    print("\n2. Testing export with date filter...")
    export_url_filtered = f"{base_url}/financial-movements/download-xlsx?start_date=2024-01-01&end_date=2024-12-31"
    
    try:
        response = requests.get(export_url_filtered, headers=headers)
        print(f"Filtered export status: {response.status_code}")
        
        if response.status_code == 200:
            content_length = len(response.content)
            print(f"Filtered export file size: {content_length} bytes")
        elif response.status_code == 404:
            print("[INFO] No movements found in date range")
        else:
            print(f"Filtered export error: {response.text}")
            
    except Exception as e:
        print(f"Filtered export request failed: {e}")

if __name__ == "__main__":
    test_excel_export()