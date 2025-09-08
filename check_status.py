#!/usr/bin/env python3
"""Verificar estado actual de la importacion"""

import requests

BACKEND_URL = "https://inmuebles-backend-api.onrender.com"
USER_EMAIL = "davsanchez21277@gmail.com"
USER_PASSWORD = "123456"

def main():
    # Login
    login_data = {"username": USER_EMAIL, "password": USER_PASSWORD}
    response = requests.post(
        f"{BACKEND_URL}/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code != 200:
        print("Login failed")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check properties
    response = requests.get(f"{BACKEND_URL}/properties", headers=headers)
    if response.status_code == 200:
        properties = response.json()
        print(f"Properties in database: {len(properties)}")
        for prop in properties:
            print(f"  - {prop.get('address', 'N/A')}")
    
    # Check mortgages
    try:
        response = requests.get(f"{BACKEND_URL}/mortgage-details", headers=headers)
        if response.status_code == 200:
            mortgages = response.json()
            print(f"\nMortgages in database: {len(mortgages)}")
    except:
        print("\nMortgages endpoint not accessible")
    
    # Check rules
    try:
        response = requests.get(f"{BACKEND_URL}/classification-rules", headers=headers)
        if response.status_code == 200:
            rules = response.json()
            print(f"\nClassification rules in database: {len(rules)}")
    except:
        print("\nRules endpoint not accessible")
    
    # Check movements
    try:
        response = requests.get(f"{BACKEND_URL}/financial-movements", headers=headers)
        if response.status_code == 200:
            movements = response.json()
            print(f"\nFinancial movements in database: {len(movements)}")
    except:
        print("\nMovements endpoint not accessible")

if __name__ == "__main__":
    main()