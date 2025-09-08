#!/usr/bin/env python3
"""Simple cleanup of production database"""

import requests
import json
import time

API = "https://inmuebles-backend-api.onrender.com"
LOCAL_API = "http://localhost:8000"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

def get_token(api_url):
    try:
        response = requests.post(
            f"{api_url}/auth/login",
            data={"username": EMAIL, "password": PASSWORD},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()["access_token"]
    except:
        pass
    return None

def main():
    print("Cleaning Production Database")
    print("=" * 40)
    
    # Get tokens
    local_token = get_token(LOCAL_API)
    prod_token = get_token(API)
    
    if not local_token or not prod_token:
        print("Login failed!")
        return
    
    print("Login OK")
    
    # Get properties from local (correct ones)
    headers_local = {"Authorization": f"Bearer {local_token}"}
    local_props = requests.get(f"{LOCAL_API}/properties", headers=headers_local).json()
    print(f"Local properties: {len(local_props)}")
    
    # Delete all properties in production
    headers_prod = {"Authorization": f"Bearer {prod_token}"}
    prod_props = requests.get(f"{API}/properties", headers=headers_prod).json()
    print(f"Production properties before: {len(prod_props)}")
    
    deleted = 0
    for prop in prod_props:
        try:
            r = requests.delete(f"{API}/properties/{prop['id']}", headers=headers_prod, timeout=10)
            if r.status_code in [200, 204]:
                deleted += 1
                print(f"Deleted: {prop['address'][:30]}")
        except:
            pass
        time.sleep(0.5)
    
    print(f"Deleted: {deleted} properties")
    time.sleep(2)
    
    # Upload correct properties
    uploaded = 0
    for prop in local_props:
        try:
            prop_data = {k: v for k, v in prop.items() if k not in ["id", "owner_id"]}
            r = requests.post(f"{API}/properties", json=prop_data, headers=headers_prod, timeout=15)
            if r.status_code in [200, 201]:
                uploaded += 1
                print(f"Uploaded: {prop.get('address', 'Unknown')[:30]}")
        except:
            pass
        time.sleep(1)
    
    print(f"Uploaded: {uploaded} properties")
    
    # Verify
    time.sleep(2)
    final_props = requests.get(f"{API}/properties", headers=headers_prod).json()
    print(f"Final count: {len(final_props)} properties")
    
    if len(final_props) == 11:
        print("SUCCESS: Exactly 11 properties!")
    else:
        print(f"WARNING: {len(final_props)} properties instead of 11")

if __name__ == "__main__":
    main()