#!/usr/bin/env python3

import requests
import json

def test_advanced_endpoints():
    """Test the advanced viability endpoints"""
    
    print("TESTING ADVANCED VIABILITY ENDPOINTS")
    print("=" * 50)
    
    # Login
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
        
        if response.status_code != 200:
            print(f"[ERROR] Login failed: {response.status_code}")
            return False
            
        token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        print(f"[OK] Login successful")
        
        # Get studies first
        response = requests.get(
            "https://inmuebles-backend-api.onrender.com/viability/",
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"[ERROR] Failed to get studies: {response.status_code}")
            return False
            
        studies = response.json()
        if not studies:
            print(f"[ERROR] No studies found")
            return False
            
        study_id = studies[0]['id']
        print(f"[OK] Using study ID: {study_id}")
        
        # Test each endpoint
        endpoints_to_test = [
            ("/summary", "GET", None),
            ("/projection?years=10", "GET", None), 
            ("/sensitivity-analysis", "POST", {}),
        ]
        
        for endpoint_path, method, body in endpoints_to_test:
            url = f"https://inmuebles-backend-api.onrender.com/viability/{study_id}{endpoint_path}"
            
            try:
                if method == "GET":
                    response = requests.get(url, headers=headers, timeout=15)
                else:
                    response = requests.post(url, headers=headers, json=body, timeout=15)
                    
                print(f"[{method}] {endpoint_path}: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"    Response size: {len(str(data))} chars")
                else:
                    print(f"    Error: {response.text[:100]}...")
                    
            except Exception as e:
                print(f"[ERROR] {endpoint_path}: {e}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == "__main__":
    test_advanced_endpoints()