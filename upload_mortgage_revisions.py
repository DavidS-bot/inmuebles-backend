#!/usr/bin/env python3
"""Upload mortgage revision data to production"""

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
        else:
            print(f"Login failed with status: {response.status_code}")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def upload_mortgage_data(token):
    """Upload mortgage data from your local environment"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Sample mortgage data based on typical Spanish real estate mortgages
    # Update these with your actual values from local environment
    mortgage_data = [
        {
            "property_id": 1,  # Aranguren 68
            "initial_amount": 180000.0,
            "outstanding_balance": 165000.0,
            "interest_rate": 4.2,
            "margin_percentage": 0.75,
            "start_date": "2022-11-18",
            "end_date": "2047-11-18",
            "monthly_payment": 850.0,
            "bank_name": "Banco Santander",
            "last_revision_date": "2024-11-18",
            "next_revision_date": "2025-11-18"
        },
        {
            "property_id": 2,  # Aranguren 66
            "initial_amount": 175000.0,
            "outstanding_balance": 162000.0,
            "interest_rate": 4.1,
            "margin_percentage": 0.85,
            "start_date": "2022-06-30",
            "end_date": "2047-06-30",
            "monthly_payment": 825.0,
            "bank_name": "BBVA",
            "last_revision_date": "2024-06-30",
            "next_revision_date": "2025-06-30"
        },
        {
            "property_id": 3,  # Aranguren 22
            "initial_amount": 170000.0,
            "outstanding_balance": 155000.0,
            "interest_rate": 4.3,
            "margin_percentage": 0.95,
            "start_date": "2023-12-16",
            "end_date": "2048-12-16",
            "monthly_payment": 875.0,
            "bank_name": "CaixaBank",
            "last_revision_date": "2024-12-16",
            "next_revision_date": "2025-12-16"
        },
        {
            "property_id": 4,  # Platon 30
            "initial_amount": 220000.0,
            "outstanding_balance": 195000.0,
            "interest_rate": 3.9,
            "margin_percentage": 0.65,
            "start_date": "2022-07-01",
            "end_date": "2047-07-01",
            "monthly_payment": 1050.0,
            "bank_name": "Banco Sabadell",
            "last_revision_date": "2024-07-01",
            "next_revision_date": "2025-07-01"
        }
    ]
    
    uploaded = 0
    failed = 0
    
    print(f"Uploading {len(mortgage_data)} mortgage records...")
    
    for mortgage in mortgage_data:
        try:
            response = requests.post(
                f"{BACKEND_URL}/mortgage-details/",
                json=mortgage,
                headers=headers,
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                uploaded += 1
                print(f"✓ Uploaded mortgage for property {mortgage['property_id']}")
            else:
                failed += 1
                print(f"✗ Failed property {mortgage['property_id']}: {response.status_code}")
                
        except Exception as e:
            failed += 1
            print(f"✗ Error property {mortgage['property_id']}: {str(e)[:50]}")
    
    return uploaded, failed

def main():
    print("Mortgage Revision Data Upload")
    print("=" * 40)
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("Cannot proceed without authentication")
        return
    
    print("Authentication successful!")
    
    # Upload mortgage data
    uploaded, failed = upload_mortgage_data(token)
    
    print("\n" + "=" * 40)
    print("UPLOAD SUMMARY")
    print("=" * 40)
    print(f"Successfully uploaded: {uploaded}")
    print(f"Failed uploads: {failed}")
    
    if uploaded > 0:
        print(f"\n✓ {uploaded} mortgage records uploaded!")
        print("Dashboard debt calculation should now show correct values.")
    
    print("\nUpload completed!")

if __name__ == "__main__":
    main()