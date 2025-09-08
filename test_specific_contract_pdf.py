#!/usr/bin/env python3
"""
Test specific contract PDF access
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
        
        pdf_url = f"{PRODUCTION_URL}/rental-contracts/{contract_id}/download-pdf"
        
        print(f"Testing contract {contract_id}:")
        print(f"URL: {pdf_url}")
        
        response = requests.get(pdf_url, headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            content_length = len(response.content)
            print(f"SUCCESS: PDF served ({content_length} bytes)")
            print(f"Content-Type: {content_type}")
            return True
        else:
            print(f"ERROR: {response.status_code}")
            if response.text:
                print(f"Error details: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    print("=== TEST SPECIFIC CONTRACT PDF ACCESS ===")
    print()
    
    token = login_to_production()
    if not token:
        return
    
    # Test contracts that have PDF paths
    test_contracts = [20, 21, 29, 31, 35, 36]
    
    success_count = 0
    for contract_id in test_contracts:
        print(f"--- Contract {contract_id} ---")
        success = test_contract_pdf_access(contract_id, token)
        if success:
            success_count += 1
        print()
    
    print(f"=== SUMMARY ===")
    print(f"Tested: {len(test_contracts)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(test_contracts) - success_count}")

if __name__ == "__main__":
    main()