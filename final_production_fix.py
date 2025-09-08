#!/usr/bin/env python3
"""Final production database fix"""

import requests
import json
import time

PROD_API = "https://inmuebles-backend-api.onrender.com"
LOCAL_API = "http://localhost:8000"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

def login(api):
    r = requests.post(f"{api}/auth/login", data={"username": EMAIL, "password": PASSWORD})
    return r.json()["access_token"] if r.status_code == 200 else None

def get_properties(api, token):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{api}/properties", headers=headers)
    return r.json() if r.status_code == 200 else []

def main():
    print("FINAL PRODUCTION FIX")
    print("=" * 30)
    
    # Check local data first
    local_token = login(LOCAL_API)
    if not local_token:
        print("Cannot connect to local backend")
        return
    
    local_props = get_properties(LOCAL_API, local_token)
    print(f"Local properties: {len(local_props)}")
    
    if len(local_props) != 11:
        print("ERROR: Local should have exactly 11 properties")
        return
    
    # Show what we have locally
    print("\nLocal properties:")
    for i, prop in enumerate(local_props, 1):
        print(f"  {i:2d}. {prop['address']}")
    
    # Now check production
    prod_token = login(PROD_API)
    if not prod_token:
        print("Cannot connect to production")
        return
    
    prod_props = get_properties(PROD_API, prod_token)
    print(f"\nProduction properties: {len(prod_props)}")
    
    if len(prod_props) == 11:
        print("Production already has correct count!")
        return
    
    # Manual approach: show what needs to be done
    print("\nSolution:")
    print("1. Go to production web interface")
    print("2. Manually delete all properties")
    print("3. Use web interface to create these 11 properties:")
    
    for i, prop in enumerate(local_props, 1):
        print(f"   {i:2d}. Address: {prop['address']}")
        if prop.get('purchase_price'):
            print(f"       Price: {prop['purchase_price']:,} EUR")
        if prop.get('property_type'):
            print(f"       Type: {prop['property_type']}")
        print()
    
    print("This is the most reliable way to ensure exactly 11 properties.")

if __name__ == "__main__":
    main()