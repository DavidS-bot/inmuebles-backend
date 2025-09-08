#!/usr/bin/env python3
"""Test mortgage endpoints specifically"""

import requests
import json
import sys

def test_mortgage_endpoints():
    """Test all mortgage-related endpoints"""
    base_url = "http://localhost:8000"
    
    # Login first
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
    
    print("Testing mortgage endpoints...")
    
    # 1. Get all properties first
    props_response = requests.get(f"{base_url}/properties/", headers=headers)
    if props_response.status_code != 200:
        print(f"Failed to get properties: {props_response.status_code}")
        return
    
    properties = props_response.json()
    print(f"Found {len(properties)} properties")
    
    # 2. Test each property's mortgage details
    for i, prop in enumerate(properties[:3]):  # Test first 3 properties
        prop_id = prop["id"]
        print(f"\n=== Testing Property {prop_id}: {prop['address'][:50]}... ===")
        
        # Get mortgage details by property
        mortgage_response = requests.get(
            f"{base_url}/mortgage-details/property/{prop_id}/details", 
            headers=headers
        )
        
        if mortgage_response.status_code == 200:
            mortgage = mortgage_response.json()
            if mortgage:
                mortgage_id = mortgage["id"]
                print(f"[OK] Mortgage found - ID: {mortgage_id}, Bank: {mortgage.get('bank_entity')}")
                print(f"  Balance: {mortgage.get('outstanding_balance')}")
                
                # Test getting revisions
                revisions_response = requests.get(
                    f"{base_url}/mortgage-details/{mortgage_id}/revisions",
                    headers=headers
                )
                
                if revisions_response.status_code == 200:
                    revisions = revisions_response.json()
                    print(f"[OK] Found {len(revisions)} revisions")
                    
                    # Show first few revisions
                    for j, rev in enumerate(revisions[:5]):
                        euribor = rev.get('euribor_rate', 'N/A')
                        margin = rev.get('margin_rate', 'N/A')
                        total_rate = None
                        if euribor != 'N/A' and margin != 'N/A' and euribor is not None and margin is not None:
                            total_rate = euribor + margin
                        print(f"    {rev['effective_date']}: Euribor {euribor}% + Margin {margin}% = {total_rate:.2f}%" if total_rate else f"    {rev['effective_date']}: Euribor {euribor}% + Margin {margin}%")
                else:
                    print(f"[ERROR] Failed to get revisions: {revisions_response.status_code}")
                    print(f"   Response: {revisions_response.text[:200]}")
            else:
                print("No mortgage found for this property")
        else:
            print(f"[ERROR] Failed to get mortgage details: {mortgage_response.status_code}")
            print(f"   Response: {mortgage_response.text[:200]}")
    
    print("\n=== Testing Euribor rates endpoint ===")
    euribor_response = requests.get(f"{base_url}/euribor-rates/", headers=headers)
    if euribor_response.status_code == 200:
        euribor_rates = euribor_response.json()
        print(f"[OK] Found {len(euribor_rates)} Euribor rates")
        
        # Show recent rates
        for rate in euribor_rates[:5]:
            print(f"    {rate['date']}: 12M = {rate.get('rate_12m', 'N/A')}%")
    else:
        print(f"[ERROR] Failed to get Euribor rates: {euribor_response.status_code}")

if __name__ == "__main__":
    test_mortgage_endpoints()