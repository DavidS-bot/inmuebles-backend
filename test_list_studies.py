#!/usr/bin/env python3

import requests
import json

# Configuration
API_BASE = "https://inmuebles-backend-api.onrender.com"
TEST_USER_EMAIL = "admin@admin.com"
TEST_USER_PASSWORD = "admin123"

def list_studies():
    """List all viability studies for admin user"""
    
    print("Listing Viability Studies for Admin User")
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
    
    # Step 2: List studies
    print("\n2. Listing viability studies...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{API_BASE}/viability/",
            headers=headers
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        
        if response.status_code == 200:
            studies = response.json()
            print(f"\nFound {len(studies)} studies:")
            
            for i, study in enumerate(studies, 1):
                print(f"\nStudy {i}:")
                print(f"  ID: {study.get('id')}")
                print(f"  Name: {study.get('study_name')}")
                print(f"  Purchase Price: EUR{study.get('purchase_price', 0):,.2f}")
                print(f"  Monthly Rent: EUR{study.get('monthly_rent', 0):,.2f}")
                
            return True
        else:
            print(f"Failed to list studies: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Request error: {e}")
        return False

if __name__ == "__main__":
    list_studies()