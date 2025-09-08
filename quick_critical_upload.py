#!/usr/bin/env python3
"""Quick upload of critical data only"""

import requests
import json

API = "https://inmuebles-backend-api.onrender.com"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

def main():
    print("Quick Critical Data Upload")
    print("-" * 40)
    
    # Load exported data
    with open("local_data_export_20250826_085725.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Login
    response = requests.post(f"{API}/auth/login", 
                            data={"username": EMAIL, "password": PASSWORD},
                            timeout=10)
    
    if response.status_code != 200:
        print("Login failed")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    print("Login successful!")
    
    # Upload only first 3 properties as test
    print("\nUploading sample properties...")
    for prop in data["properties"][:3]:
        prop_data = {k: v for k, v in prop.items() if k != "id"}
        try:
            r = requests.post(f"{API}/properties", json=prop_data, headers=headers, timeout=15)
            print(f"Property: {r.status_code} - {prop.get('address', 'Unknown')[:30]}")
        except Exception as e:
            print(f"Error: {str(e)[:30]}")
    
    # Upload sample mortgages
    print("\nUploading sample mortgages...")
    for mort in data["mortgages"][:2]:
        mort_data = {k: v for k, v in mort.items() if k != "id"}
        try:
            r = requests.post(f"{API}/mortgage-details/", json=mort_data, headers=headers, timeout=15)
            print(f"Mortgage: {r.status_code} - Property {mort.get('property_id')}")
        except Exception as e:
            print(f"Error: {str(e)[:30]}")
    
    print("\nQuick upload completed!")
    print("Check the dashboard for updated data.")

if __name__ == "__main__":
    main()