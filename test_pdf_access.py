#!/usr/bin/env python3
"""
Test PDF access in production
"""

import requests

PRODUCTION_URL = "https://inmuebles-backend-api.onrender.com"

def login_to_production() -> str:
    """Login and get token"""
    try:
        response = requests.post(
            f"{PRODUCTION_URL}/auth/login",
            data={
                'username': 'davsanchez21277@gmail.com',
                'password': '123456'
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('access_token')
        else:
            print(f"ERROR login: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"ERROR login: {e}")
        return None

def test_contract_pdf_access(contract_id: int, token: str):
    """Test accessing a contract PDF"""
    try:
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test the download endpoint
        pdf_url = f"{PRODUCTION_URL}/rental-contracts/{contract_id}/download-pdf"
        
        print(f"Testing PDF access for contract {contract_id}:")
        print(f"URL: {pdf_url}")
        
        response = requests.get(pdf_url, headers=headers)
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'pdf' in content_type.lower():
                print(f"SUCCESS: PDF served correctly ({len(response.content)} bytes)")
                return True
            else:
                print(f"ERROR: Not a PDF response, got: {content_type}")
                print(f"Content preview: {response.text[:200]}...")
                return False
        else:
            print(f"ERROR: {response.status_code}")
            if response.text:
                print(f"Error details: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERROR testing PDF access: {e}")
        return False

def main():
    print("=== TEST PDF ACCESS IN PRODUCTION ===")
    print()
    
    # Login
    token = login_to_production()
    if not token:
        print("Cannot proceed without login")
        return
    
    print("Login successful!")
    print()
    
    # Test a few contract IDs
    test_contracts = [1, 2, 4, 5, 6]
    
    for contract_id in test_contracts:
        print(f"--- Testing Contract {contract_id} ---")
        success = test_contract_pdf_access(contract_id, token)
        print(f"Result: {'PASS' if success else 'FAIL'}")
        print()

if __name__ == "__main__":
    main()