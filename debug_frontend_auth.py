#!/usr/bin/env python3

import requests
import json

def debug_frontend_auth():
    """Debug frontend authentication and data flow"""
    
    print("DEBUGGING FRONTEND AUTHENTICATION")
    print("=" * 50)
    
    # Test the exact same flow the frontend uses
    print("1. Testing frontend login flow...")
    
    # First, check if the user exists
    login_data = {
        "username": "davsanchez21277@gmail.com",
        "password": "123456"
    }
    
    try:
        response = requests.post(
            "https://inmuebles-backend-api.onrender.com/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"Login response status: {response.status_code}")
        print(f"Login response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"Login success: {json.dumps(token_data, indent=2)}")
            
            token = token_data.get("access_token")
            token_type = token_data.get("token_type", "bearer")
            
        else:
            print(f"Login failed: {response.text}")
            return
            
    except Exception as e:
        print(f"Login error: {e}")
        return
    
    # Test the viability endpoint exactly as frontend would
    print(f"\n2. Testing viability endpoint with token...")
    
    headers = {
        "Authorization": f"{token_type} {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(
            "https://inmuebles-backend-api.onrender.com/viability/",
            headers=headers
        )
        
        print(f"Viability response status: {response.status_code}")
        print(f"Viability response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            studies = response.json()
            print(f"Studies found: {len(studies)}")
            
            if len(studies) > 0:
                print("Study details:")
                for i, study in enumerate(studies, 1):
                    print(f"  Study {i}:")
                    print(f"    ID: {study.get('id')}")
                    print(f"    Name: {study.get('study_name')}")
                    print(f"    User ID: {study.get('user_id')}")
                    print(f"    Purchase Price: {study.get('purchase_price')}")
                    print(f"    Monthly Rent: {study.get('monthly_rent')}")
                    print(f"    Net Return: {study.get('net_annual_return')}")
                    print(f"    Risk Level: {study.get('risk_level')}")
            else:
                print("No studies returned!")
                
        else:
            print(f"Viability failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Viability error: {e}")
    
    # Test auth endpoint
    print(f"\n3. Testing auth verification endpoint...")
    
    try:
        response = requests.get(
            "https://inmuebles-backend-api.onrender.com/test-auth",
            headers=headers
        )
        
        print(f"Auth test status: {response.status_code}")
        
        if response.status_code == 200:
            auth_data = response.json()
            print(f"Auth verification: {json.dumps(auth_data, indent=2)}")
        else:
            print(f"Auth test failed: {response.text}")
            
    except Exception as e:
        print(f"Auth test error: {e}")
    
    # Check CORS headers
    print(f"\n4. Testing CORS...")
    
    try:
        response = requests.options(
            "https://inmuebles-backend-api.onrender.com/viability/",
            headers={
                "Origin": "https://inmuebles-web.vercel.app",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization,content-type"
            }
        )
        
        print(f"CORS preflight status: {response.status_code}")
        cors_headers = {k: v for k, v in response.headers.items() if 'access-control' in k.lower()}
        print(f"CORS headers: {cors_headers}")
        
    except Exception as e:
        print(f"CORS test error: {e}")

if __name__ == "__main__":
    debug_frontend_auth()