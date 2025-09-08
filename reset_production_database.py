#!/usr/bin/env python3
"""Complete database reset"""

import requests
import time

API = "https://inmuebles-backend-api.onrender.com"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

def get_token():
    response = requests.post(f"{API}/auth/login", data={"username": EMAIL, "password": PASSWORD})
    return response.json()["access_token"] if response.status_code == 200 else None

def delete_all_data(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    # Delete all properties (this should cascade delete related data)
    properties = requests.get(f"{API}/properties", headers=headers).json()
    print(f"Deleting {len(properties)} properties...")
    
    for prop in properties:
        try:
            requests.delete(f"{API}/properties/{prop['id']}", headers=headers, timeout=10)
            print(f"Deleted property {prop['id']}")
        except:
            pass
        time.sleep(0.3)
    
    # Delete mortgages
    try:
        mortgages = requests.get(f"{API}/mortgage-details/", headers=headers).json()
        print(f"Deleting {len(mortgages)} mortgages...")
        for mort in mortgages:
            requests.delete(f"{API}/mortgage-details/{mort['id']}", headers=headers)
            time.sleep(0.3)
    except:
        pass
    
    # Delete contracts
    try:
        contracts = requests.get(f"{API}/rental-contracts", headers=headers).json()
        print(f"Deleting {len(contracts)} contracts...")
        for contract in contracts:
            requests.delete(f"{API}/rental-contracts/{contract['id']}", headers=headers)
            time.sleep(0.3)
    except:
        pass
    
    print("Database cleanup completed")

def main():
    print("COMPLETE DATABASE RESET")
    print("=" * 30)
    
    token = get_token()
    if not token:
        print("Login failed")
        return
    
    print("Login successful")
    
    # Multiple cleanup passes
    for i in range(3):
        print(f"\nCleanup pass {i+1}...")
        delete_all_data(token)
        time.sleep(3)
    
    # Verify
    headers = {"Authorization": f"Bearer {token}"}
    properties = requests.get(f"{API}/properties", headers=headers).json()
    print(f"\nFinal verification: {len(properties)} properties remain")
    
    if len(properties) == 0:
        print("SUCCESS: Database is clean!")
    else:
        print("WARNING: Some data remains")

if __name__ == "__main__":
    main()