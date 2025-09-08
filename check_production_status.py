#!/usr/bin/env python3
"""Check production status"""

import requests

PROD_API = "https://inmuebles-backend-api.onrender.com"

def check_status():
    print("PRODUCTION STATUS CHECK")
    print("=" * 30)
    
    try:
        # Test login
        response = requests.post(f"{PROD_API}/auth/login", 
                               data={"username": "davsanchez21277@gmail.com", "password": "123456"})
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("Login: OK")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # Check properties
            props = requests.get(f"{PROD_API}/properties", headers=headers).json()
            print(f"Properties: {len(props)}")
            
            # Check mortgages 
            try:
                mortgages = requests.get(f"{PROD_API}/mortgage-details/", headers=headers).json()
                print(f"Mortgages: {len(mortgages)}")
            except:
                print("Mortgages: Error")
            
            # Check contracts
            try:
                contracts = requests.get(f"{PROD_API}/rental-contracts", headers=headers).json()
                print(f"Contracts: {len(contracts)}")
            except:
                print("Contracts: Error")
                
        else:
            print("Login: FAILED")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_status()