#!/usr/bin/env python3
"""Test endpoints simple"""

import requests

def test():
    # Login
    response = requests.post("https://inmuebles-backend-api.onrender.com/auth/login", 
                           data={"username": "davsanchez21277@gmail.com", "password": "123456"})
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test mortgage endpoints
    print("Testing /mortgage-details (without slash):")
    r1 = requests.get("https://inmuebles-backend-api.onrender.com/mortgage-details", headers=headers)
    print(f"  Status: {r1.status_code}")
    
    print("Testing /mortgage-details/ (with slash):")
    r2 = requests.get("https://inmuebles-backend-api.onrender.com/mortgage-details/", headers=headers)
    print(f"  Status: {r2.status_code}")
    if r2.status_code == 200:
        data = r2.json()
        print(f"  Items: {len(data)}")
        total_debt = sum(item.get('outstanding_balance', 0) for item in data)
        print(f"  Total debt: {total_debt:.2f} EUR")

if __name__ == "__main__":
    test()