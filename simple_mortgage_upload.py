#!/usr/bin/env python3
"""Simple mortgage data upload"""

import requests
import json

BACKEND_URL = "https://inmuebles-backend-api.onrender.com"
USER_EMAIL = "davsanchez21277@gmail.com"
USER_PASSWORD = "123456"

def get_auth_token():
    try:
        login_data = {"username": USER_EMAIL, "password": USER_PASSWORD}
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def main():
    print("Simple Mortgage Upload")
    
    token = get_auth_token()
    if not token:
        print("Login failed")
        return
    
    print("Login OK")
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Key mortgage data for main properties
    mortgages = [
        {
            "property_id": 1,
            "initial_amount": 180000.0,
            "outstanding_balance": 165000.0,
            "interest_rate": 4.2,
            "margin_percentage": 0.75,
            "start_date": "2022-11-18",
            "end_date": "2047-11-18",
            "monthly_payment": 850.0,
            "bank_name": "Banco Santander"
        },
        {
            "property_id": 2,
            "initial_amount": 175000.0,
            "outstanding_balance": 162000.0,
            "interest_rate": 4.1,
            "margin_percentage": 0.85,
            "start_date": "2022-06-30",
            "end_date": "2047-06-30",
            "monthly_payment": 825.0,
            "bank_name": "BBVA"
        }
    ]
    
    uploaded = 0
    for mortgage in mortgages:
        try:
            response = requests.post(
                f"{BACKEND_URL}/mortgage-details/",
                json=mortgage,
                headers=headers,
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                uploaded += 1
                print(f"OK: Property {mortgage['property_id']}")
            else:
                print(f"FAIL: Property {mortgage['property_id']} - {response.status_code}")
                
        except Exception as e:
            print(f"ERROR: Property {mortgage['property_id']} - {str(e)[:30]}")
    
    print(f"Uploaded: {uploaded}/{len(mortgages)}")

if __name__ == "__main__":
    main()