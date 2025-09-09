#!/usr/bin/env python3

import requests
import json

def debug_frontend_connection():
    """Debug why frontend can't see the studies"""
    
    print("DEBUGGING FRONTEND CONNECTION")
    print("=" * 50)
    
    # Test different login scenarios
    test_users = [
        {"email": "admin@admin.com", "password": "admin123", "name": "Admin User"},
        {"email": "test@test.com", "password": "test123", "name": "Test User"},
        {"email": "davsanchez21277@gmail.com", "password": "123456", "name": "Main User"}
    ]
    
    for user in test_users:
        print(f"\n=== Testing {user['name']} ===")
        
        # Login
        login_data = {
            "username": user["email"],
            "password": user["password"]
        }
        
        try:
            response = requests.post(
                "https://inmuebles-backend-api.onrender.com/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code != 200:
                print(f"  Login failed: {response.status_code}")
                continue
                
            token = response.json().get("access_token")
            user_id = response.json().get("user_id", "unknown")
            print(f"  Login successful - User ID: {user_id}")
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Check viability studies
            response = requests.get(
                "https://inmuebles-backend-api.onrender.com/viability/",
                headers=headers
            )
            
            if response.status_code == 200:
                studies = response.json()
                print(f"  Viability studies: {len(studies)}")
                for study in studies:
                    print(f"    - {study.get('study_name')} (User: {study.get('user_id')})")
            else:
                print(f"  Failed to get studies: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"  Error: {e}")
    
    # Check what user_id the studies belong to
    print(f"\n=== Direct Database Check ===")
    try:
        # Use admin to check all studies
        login_data = {"username": "admin@admin.com", "password": "admin123"}
        response = requests.post(
            "https://inmuebles-backend-api.onrender.com/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Use debug endpoint to see all routes
            response = requests.get(
                "https://inmuebles-backend-api.onrender.com/debug/routes",
                headers=headers
            )
            
            if response.status_code == 200:
                routes = response.json()
                viability_routes = [r for r in routes.get('routes', []) if 'viability' in r.get('path', '')]
                print(f"  Available viability routes: {len(viability_routes)}")
                for route in viability_routes:
                    print(f"    {route.get('methods')} {route.get('path')}")
            
    except Exception as e:
        print(f"  Error checking routes: {e}")

if __name__ == "__main__":
    debug_frontend_connection()