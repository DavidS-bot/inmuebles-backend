import requests
import time

API = "https://inmuebles-backend-api.onrender.com"
EMAIL = "davsanchez21277@gmail.com"  
PASS = "123456"

def get_token():
    r = requests.post(f"{API}/auth/login", data={"username": EMAIL, "password": PASS}, timeout=10)
    return r.json()["access_token"] if r.status_code == 200 else None

token = get_token()
if token:
    print("Connected to production!")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Add sample mortgage (will fix debt = 0 issue)
    mortgage = {
        "property_id": 1, 
        "outstanding_balance": 165000,
        "initial_amount": 180000,
        "bank_name": "Banco Test"
    }
    
    try:
        r = requests.post(f"{API}/mortgage-details/", json=mortgage, headers=headers, timeout=15)
        print(f"Mortgage upload: {r.status_code}")
    except:
        print("Mortgage upload failed")
    
    print("Data upload attempt completed")
else:
    print("Login failed")