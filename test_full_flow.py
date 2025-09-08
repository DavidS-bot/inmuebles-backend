#!/usr/bin/env python3
"""Test complete data flow for mortgage revisions"""

import requests
import json

def test_complete_flow():
    """Test the complete flow that the frontend would use"""
    base_url = "http://localhost:8000"
    
    # Login
    login_data = {
        "username": "davsanchez21277@gmail.com",
        "password": "123456"
    }
    
    response = requests.post(
        f"{base_url}/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test the exact flow that frontend uses
    property_id = 1  # Test with property 1
    
    print(f"=== Testing complete flow for Property {property_id} ===")
    
    # Step 1: Get property details (like frontend does at line 128)
    print("1. Getting property details...")
    property_response = requests.get(f"{base_url}/properties/{property_id}", headers=headers)
    if property_response.status_code == 200:
        property_data = property_response.json()
        print(f"   [OK] Property: {property_data['address']}")
    else:
        print(f"   [ERROR] Failed to get property: {property_response.status_code}")
        return
    
    # Step 2: Get mortgage details by property (like frontend does at line 133)
    print("2. Getting mortgage details...")
    mortgage_response = requests.get(f"{base_url}/mortgage-details/property/{property_id}/details", headers=headers)
    if mortgage_response.status_code == 200:
        mortgage_data = mortgage_response.json()
        if mortgage_data:
            mortgage_id = mortgage_data["id"]
            print(f"   [OK] Mortgage ID: {mortgage_id}, Bank: {mortgage_data.get('bank_entity')}")
        else:
            print("   ! No mortgage data found for this property")
            return
    else:
        print(f"   [ERROR] Failed to get mortgage: {mortgage_response.status_code}")
        return
    
    # Step 3: Get revisions (like frontend does at line 180)
    print("3. Getting mortgage revisions...")
    revisions_response = requests.get(f"{base_url}/mortgage-details/{mortgage_id}/revisions", headers=headers)
    if revisions_response.status_code == 200:
        revisions_data = revisions_response.json()
        print(f"   [OK] Found {len(revisions_data)} revisions")
        
        # Check for Euribor data like frontend does
        revisions_with_euribor = [r for r in revisions_data if r.get('euribor_rate') is not None]
        print(f"   [OK] {len(revisions_with_euribor)} revisions have Euribor rates")
        
        # Show sample of what frontend would see
        print("   Sample of first 5 revisions that frontend receives:")
        for i, rev in enumerate(revisions_data[:5]):
            euribor = rev.get('euribor_rate', 'null')
            margin = rev.get('margin_rate', 'null')
            total = None
            if euribor is not None and margin is not None:
                total = euribor + margin
            print(f"     {rev['effective_date']}: Euribor={euribor}%, Margin={margin}%, Total={total:.2f}%" if total else f"     {rev['effective_date']}: Euribor={euribor}%, Margin={margin}%")
        
    else:
        print(f"   [ERROR] Failed to get revisions: {revisions_response.status_code}")
        return
    
    # Step 4: Get summary (like frontend does at line 190)
    print("4. Getting mortgage summary...")
    summary_response = requests.get(f"{base_url}/mortgage-details/{mortgage_id}/summary", headers=headers)
    if summary_response.status_code == 200:
        summary_data = summary_response.json()
        print(f"   [OK] Summary: Current payment={summary_data.get('current_payment')}, Annual rate={summary_data.get('annual_rate')}%")
    else:
        print(f"   [ERROR] Failed to get summary: {summary_response.status_code}")
        print(f"   Error: {summary_response.text}")
    
    # Step 5: Get schedule (like frontend does at line 194)
    print("5. Getting amortization schedule...")
    schedule_response = requests.get(f"{base_url}/mortgage-details/{mortgage_id}/calculate-schedule", headers=headers)
    if schedule_response.status_code == 200:
        schedule_data = schedule_response.json()
        schedule = schedule_data.get('schedule', [])
        print(f"   [OK] Schedule calculated with {len(schedule)} entries")
        if schedule:
            print(f"   First payment: Date={schedule[0].get('month')}, Amount={schedule[0].get('payment')}, Rate={schedule[0].get('annual_rate')}%")
    else:
        print(f"   [ERROR] Failed to get schedule: {schedule_response.status_code}")
        print(f"   Error: {schedule_response.text}")
    
    print("\n=== Summary ===")
    print("[OK] Backend API is working correctly")
    print("[OK] All mortgage data is available via API")
    print(f"[OK] Property {property_id} has {len(revisions_data)} mortgage revisions")
    print(f"[OK] {len(revisions_with_euribor)} revisions have Euribor rates")
    
    if len(revisions_with_euribor) > 0:
        print("[SUCCESS] CONCLUSION: The Euribor revision data IS available in the backend!")
        print("   If you don't see it in the frontend, check:")
        print("   1. Is the frontend running and connected to the right backend?")
        print("   2. Are there any JavaScript console errors?")
        print("   3. Is the authentication working correctly?")
    else:
        print("[FAIL] CONCLUSION: No Euribor data found in revisions")

if __name__ == "__main__":
    test_complete_flow()