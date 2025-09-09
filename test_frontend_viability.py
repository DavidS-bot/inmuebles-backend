#!/usr/bin/env python3

import requests
import json

# Configuration
API_BASE = "https://inmuebles-backend-api.onrender.com"
TEST_USER_EMAIL = "admin@admin.com"
TEST_USER_PASSWORD = "admin123"

def test_frontend_data():
    """Test what frontend should see"""
    
    print("TESTING FRONTEND VIABILITY DATA")
    print("=" * 50)
    
    # Step 1: Login
    print("1. Logging in as admin...")
    login_data = {
        "username": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code != 200:
            print(f"Login failed: {response.status_code}")
            return False
            
        token = response.json().get("access_token")
        print(f"Login successful")
        
    except Exception as e:
        print(f"Login error: {e}")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Step 2: Check viability studies
    print("\n2. Checking viability studies...")
    try:
        response = requests.get(f"{API_BASE}/viability/", headers=headers)
        print(f"Viability endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            studies = response.json()
            print(f"Found {len(studies)} viability studies")
            for study in studies:
                print(f"  - {study.get('study_name')} (ID: {study.get('id')})")
        else:
            print(f"Error getting studies: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Step 3: Check classification rules
    print("\n3. Checking classification rules...")
    try:
        response = requests.get(f"{API_BASE}/classification-rules/", headers=headers)
        print(f"Classification rules endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            rules = response.json()
            print(f"Found {len(rules)} classification rules")
            for rule in rules:
                print(f"  - {rule.get('rule_name')} -> {rule.get('category')}")
        else:
            print(f"Error getting rules: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Step 4: Check if auth is working for frontend
    print("\n4. Testing auth endpoint...")
    try:
        response = requests.get(f"{API_BASE}/test-auth", headers=headers)
        print(f"Auth test status: {response.status_code}")
        
        if response.status_code == 200:
            auth_data = response.json()
            print(f"Auth working for user: {auth_data.get('user_email')}")
        else:
            print(f"Auth test failed: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Step 5: Create a test classification rule
    print("\n5. Creating test classification rule...")
    rule_data = {
        "rule_name": "Test Rule - Alquiler",
        "pattern": "alquiler",
        "category": "Ingresos por Alquiler",
        "is_active": True
    }
    
    try:
        response = requests.post(f"{API_BASE}/classification-rules/", headers=headers, json=rule_data)
        print(f"Rule creation status: {response.status_code}")
        
        if response.status_code == 200:
            rule = response.json()
            print(f"Rule created: {rule.get('rule_name')} (ID: {rule.get('id')})")
        else:
            print(f"Rule creation failed: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_frontend_data()