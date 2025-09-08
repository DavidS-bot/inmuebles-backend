#!/usr/bin/env python3
"""
Simulate exactly what the frontend does when clicking the Bankinter button
"""

import requests
import json

def simulate_frontend_request():
    """Simulate the exact frontend request flow"""
    
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    print("Simulating frontend Bankinter button click...")
    print(f"Backend URL: {backend_url}")
    
    # Step 1: Login (same as frontend would do)
    print("\n1. Frontend login simulation...")
    
    # Try different login methods the frontend might use
    login_endpoints = [
        ('/auth/login', {'username': 'davsanchez21277@gmail.com', 'password': '123456'}),
    ]
    
    token = None
    for endpoint, data in login_endpoints:
        print(f"   Trying {endpoint}...")
        try:
            # Try form data (like frontend)
            response = requests.post(
                f'{backend_url}{endpoint}',
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                token = result.get('access_token')
                print(f"   ✅ Login successful with {endpoint}")
                break
            else:
                print(f"   ❌ {endpoint} failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {endpoint} exception: {e}")
    
    if not token:
        print("❌ Could not login with any method")
        return
    
    # Step 2: Make the Bankinter request exactly like frontend
    print("\n2. Frontend Bankinter request simulation...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    
    print(f"   Headers: {headers}")
    print(f"   URL: {backend_url}/integrations/bankinter/sync-now")
    
    try:
        # Exact request the frontend makes
        response = requests.post(
            f'{backend_url}/integrations/bankinter/sync-now',
            headers=headers,
            json={},  # Empty JSON body like frontend
            timeout=180  # 3 minutes like frontend
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ SUCCESS! Response:")
            print(f"   {json.dumps(result, indent=4)}")
        else:
            print(f"   ❌ FAILED! Response:")
            print(f"   Status: {response.status_code}")
            print(f"   Text: {response.text}")
            
            try:
                error_json = response.json()
                print(f"   JSON Error: {json.dumps(error_json, indent=4)}")
            except:
                pass
                
    except requests.exceptions.Timeout:
        print("   ⏰ Request timed out (this might be normal for long operations)")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simulate_frontend_request()