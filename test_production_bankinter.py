#!/usr/bin/env python3
"""
Test the production Bankinter endpoint
"""
import requests

def test_production_endpoint():
    """Test the fixed Bankinter endpoint in production"""
    
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    print("Testing production Bankinter sync endpoint...")
    
    try:
        # Login first
        login_data = {
            'username': 'davsanchez21277@gmail.com',
            'password': '123456'
        }
        
        print("1. Logging in...")
        login_response = requests.post(
            f'{backend_url}/auth/login',
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return False
        
        token = login_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        print("2. Login successful! Testing Bankinter sync...")
        
        # Test Bankinter sync
        sync_response = requests.post(
            f'{backend_url}/integrations/bankinter/sync-now',
            headers=headers,
            json={},
            timeout=180  # 3 minute timeout
        )
        
        print(f"3. Sync response status: {sync_response.status_code}")
        
        if sync_response.status_code == 200:
            result = sync_response.json()
            print("4. SUCCESS! Bankinter sync result:")
            print(f"   Status: {result.get('sync_status')}")
            print(f"   Message: {result.get('message')}")
            
            if 'new_movements' in result:
                print(f"   New movements: {result.get('new_movements')}")
                print(f"   Total rows: {result.get('total_rows')}")
                print(f"   Duplicates skipped: {result.get('duplicates_skipped')}")
            
            return True
        else:
            print(f"4. Sync failed: {sync_response.status_code}")
            print(f"   Response: {sync_response.text}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = test_production_endpoint()
    if success:
        print("\nSUCCESS: PRODUCTION BANKINTER ENDPOINT IS WORKING!")
    else:
        print("\nFAILED: Production endpoint failed")