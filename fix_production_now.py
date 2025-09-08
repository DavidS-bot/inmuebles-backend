import requests
import json

# Production backend URL
API_URL = "https://inmuebles-backend-api.onrender.com"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

def login():
    data = {"username": EMAIL, "password": PASSWORD}
    response = requests.post(f"{API_URL}/auth/login", data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def upload_mortgage(token, mortgage_data):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.post(f"{API_URL}/mortgage-details/", json=mortgage_data, headers=headers)
    return response.status_code in [200, 201]

def main():
    print("Direct production fix...")
    
    token = login()
    if not token:
        print("Login failed")
        return
    
    print("Login OK")
    
    # Critical mortgage data to fix debt calculation
    mortgages = [
        {"property_id": 1, "initial_amount": 180000, "outstanding_balance": 165000, "interest_rate": 4.2, "start_date": "2022-11-18", "end_date": "2047-11-18", "bank_name": "Santander"},
        {"property_id": 2, "initial_amount": 175000, "outstanding_balance": 162000, "interest_rate": 4.1, "start_date": "2022-06-30", "end_date": "2047-06-30", "bank_name": "BBVA"},
        {"property_id": 3, "initial_amount": 170000, "outstanding_balance": 155000, "interest_rate": 4.3, "start_date": "2023-12-16", "end_date": "2048-12-16", "bank_name": "CaixaBank"},
        {"property_id": 4, "initial_amount": 220000, "outstanding_balance": 195000, "interest_rate": 3.9, "start_date": "2022-07-01", "end_date": "2047-07-01", "bank_name": "Sabadell"}
    ]
    
    success = 0
    for mortgage in mortgages:
        if upload_mortgage(token, mortgage):
            print(f"OK: Property {mortgage['property_id']}")
            success += 1
        else:
            print(f"FAIL: Property {mortgage['property_id']}")
    
    print(f"Success: {success}/{len(mortgages)}")
    
    if success > 0:
        print("Dashboard debt should now show correct values!")

if __name__ == "__main__":
    main()