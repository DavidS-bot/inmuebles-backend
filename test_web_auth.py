#!/usr/bin/env python3
"""
Test web authentication and session
"""

import requests
import json

def test_web_auth():
    """Test authentication flow that the web might be using"""
    
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    print("Testing web authentication...")
    
    # Test 1: Check if user exists and credentials work
    print("\n1. Testing login credentials...")
    
    login_data = {'username': 'davsanchez21277@gmail.com', 'password': '123456'}
    
    try:
        response = requests.post(
            f'{backend_url}/auth/login',
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        print(f"Login response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            token = result.get('access_token')
            token_type = result.get('token_type', 'bearer')
            
            print(f"Token type: {token_type}")
            print(f"Token length: {len(token) if token else 0}")
            print(f"Token starts with: {token[:20]}..." if token else "No token")
            
            # Test 2: Verify token works for protected endpoints
            print("\n2. Testing token authentication...")
            
            # Test different auth header formats
            auth_formats = [
                f'Bearer {token}',
                f'bearer {token}',
                f'{token_type} {token}',
                f'{token}'
            ]
            
            for auth_header in auth_formats:
                print(f"   Trying: {auth_header[:30]}...")
                
                try:
                    test_response = requests.get(
                        f'{backend_url}/properties',  # Simple protected endpoint
                        headers={'Authorization': auth_header},
                        timeout=10
                    )
                    
                    if test_response.status_code == 200:
                        print(f"   SUCCESS with: {auth_header[:30]}...")
                        
                        # Now test Bankinter endpoint with this format
                        print("\n3. Testing Bankinter with working auth...")
                        
                        bankinter_response = requests.post(
                            f'{backend_url}/integrations/bankinter/sync-now',
                            headers={
                                'Authorization': auth_header,
                                'Content-Type': 'application/json'
                            },
                            json={},
                            timeout=30
                        )
                        
                        print(f"   Bankinter status: {bankinter_response.status_code}")
                        if bankinter_response.status_code == 200:
                            print("   Bankinter SUCCESS!")
                            bankinter_result = bankinter_response.json()
                            for key, value in bankinter_result.items():
                                print(f"     {key}: {value}")
                        else:
                            print(f"   Bankinter FAILED: {bankinter_response.text}")
                        
                        return  # Exit on first success
                        
                    else:
                        print(f"   Failed: {test_response.status_code}")
                        
                except Exception as e:
                    print(f"   Exception: {e}")
            
        else:
            print(f"Login failed: {response.text}")
            
    except Exception as e:
        print(f"Login exception: {e}")

if __name__ == "__main__":
    test_web_auth()