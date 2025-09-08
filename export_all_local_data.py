#!/usr/bin/env python3
"""Export ALL data from local backend"""

import requests
import json
from datetime import datetime

LOCAL_API = "http://localhost:8000"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

def get_token():
    try:
        response = requests.post(
            f"{LOCAL_API}/auth/login",
            data={"username": EMAIL, "password": PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()["access_token"]
    except Exception as e:
        print(f"Login error: {e}")
    return None

def export_all_data(token):
    headers = {"Authorization": f"Bearer {token}"}
    data = {}
    
    # Properties
    try:
        r = requests.get(f"{LOCAL_API}/properties", headers=headers)
        if r.status_code == 200:
            data["properties"] = r.json()
            print(f"Exported {len(data['properties'])} properties")
    except Exception as e:
        print(f"Error exporting properties: {e}")
    
    # Mortgage details
    try:
        r = requests.get(f"{LOCAL_API}/mortgage-details/", headers=headers)
        if r.status_code == 200:
            data["mortgages"] = r.json()
            print(f"Exported {len(data['mortgages'])} mortgages")
    except Exception as e:
        print(f"Error exporting mortgages: {e}")
    
    # Rental contracts
    try:
        r = requests.get(f"{LOCAL_API}/rental-contracts", headers=headers)
        if r.status_code == 200:
            data["contracts"] = r.json()
            print(f"Exported {len(data['contracts'])} rental contracts")
    except Exception as e:
        print(f"Error exporting contracts: {e}")
    
    # Financial movements
    try:
        r = requests.get(f"{LOCAL_API}/financial-movements", headers=headers)
        if r.status_code == 200:
            data["movements"] = r.json()
            print(f"Exported {len(data['movements'])} financial movements")
    except Exception as e:
        print(f"Error exporting movements: {e}")
    
    # Classification rules
    try:
        r = requests.get(f"{LOCAL_API}/classification-rules", headers=headers)
        if r.status_code == 200:
            data["rules"] = r.json()
            print(f"Exported {len(data['rules'])} classification rules")
    except Exception as e:
        print(f"Error exporting rules: {e}")
    
    # Euribor rates
    try:
        r = requests.get(f"{LOCAL_API}/euribor-rates", headers=headers)
        if r.status_code == 200:
            data["euribor"] = r.json()
            print(f"Exported {len(data['euribor'])} euribor rates")
    except Exception as e:
        print(f"Error exporting euribor: {e}")
    
    return data

def main():
    print("=" * 50)
    print("LOCAL DATA EXPORT")
    print("=" * 50)
    
    token = get_token()
    if not token:
        print("Failed to authenticate with local backend")
        return
    
    print("Authentication successful!")
    print("Exporting all data from local backend...")
    
    data = export_all_data(token)
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"local_data_export_{timestamp}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\nData exported to: {filename}")
    print(f"Total records exported:")
    for key in data:
        print(f"  - {key}: {len(data[key])}")

if __name__ == "__main__":
    main()