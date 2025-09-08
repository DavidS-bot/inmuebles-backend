#!/usr/bin/env python3
"""Verify what data is actually in production"""

import requests
import json

PROD_API = "https://inmuebles-backend-api.onrender.com"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

def login():
    try:
        response = requests.post(f"{PROD_API}/auth/login", 
                               data={"username": EMAIL, "password": PASSWORD}, timeout=15)
        return response.json()["access_token"] if response.status_code == 200 else None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def check_data():
    token = login()
    if not token:
        print("Login failed")
        return
        
    headers = {"Authorization": f"Bearer {token}"}
    
    print("PRODUCTION DATA STATUS")
    print("=" * 30)
    
    # Check each endpoint
    endpoints = [
        "/properties",
        "/mortgage-details/", 
        "/rental-contracts",
        "/financial-movements"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{PROD_API}{endpoint}", headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                print(f"{endpoint}: {len(data)} items")
                if endpoint == "/mortgage-details/" and data:
                    total_debt = sum(item.get('outstanding_balance', 0) for item in data)
                    print(f"  Total Debt: {total_debt:,.2f} EUR")
            else:
                print(f"{endpoint}: ERROR {response.status_code}")
        except Exception as e:
            print(f"{endpoint}: TIMEOUT/ERROR")
    
    # Test classification rules endpoint
    print("\nTesting classification-rules endpoint:")
    try:
        response = requests.get(f"{PROD_API}/classification-rules", headers=headers, timeout=10)
        print(f"GET /classification-rules: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Found: {len(data)} rules")
    except:
        print("GET /classification-rules: TIMEOUT")
    
    # Test POST to classification rules
    try:
        test_rule = {
            "rule_name": "Test Rule",
            "pattern": "test",
            "category": "Test", 
            "subcategory": "Test",
            "priority": 1,
            "is_active": True
        }
        headers_post = {**headers, "Content-Type": "application/json"}
        response = requests.post(f"{PROD_API}/classification-rules", 
                               json=test_rule, headers=headers_post, timeout=10)
        print(f"POST /classification-rules: {response.status_code}")
        if response.status_code not in [200, 201]:
            print(f"  Response: {response.text[:100]}")
    except Exception as e:
        print(f"POST /classification-rules: ERROR - {e}")

if __name__ == "__main__":
    check_data()