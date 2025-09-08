#!/usr/bin/env python3
"""Test script to authenticate and get a token for testing APIs"""

import requests
import json
import sys

def test_auth_and_get_token():
    """Test authentication and get a token"""
    base_url = "http://localhost:8000"
    
    # First, create a user if doesn't exist (using the default user script logic)
    import sqlite3
    from app.auth import hash_password
    
    conn = sqlite3.connect('data/dev.db')
    cursor = conn.cursor()
    
    email = "davsanchez21277@gmail.com"
    password = "123456"
    
    # Check if user exists
    cursor.execute("SELECT id FROM user WHERE email = ?", (email,))
    user = cursor.fetchone()
    
    if not user:
        # Create user
        hashed_password = hash_password(password)
        cursor.execute("""
            INSERT INTO user (email, hashed_password, is_active)
            VALUES (?, ?, 1)
        """, (email, hashed_password))
        conn.commit()
        print(f"Created user: {email}")
    else:
        print(f"User exists: {email}")
    
    conn.close()
    
    # Now test login
    login_data = {
        "username": email,
        "password": password
    }
    
    print("Testing login...")
    response = requests.post(
        f"{base_url}/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data["access_token"]
        print(f"Login successful! Token: {access_token[:50]}...")
        
        # Test an authenticated endpoint
        headers = {"Authorization": f"Bearer {access_token}"}
        
        print("\nTesting properties endpoint...")
        properties_response = requests.get(f"{base_url}/properties/", headers=headers)
        if properties_response.status_code == 200:
            properties = properties_response.json()
            print(f"Found {len(properties)} properties")
            
            # Test mortgage details for first property
            if properties:
                prop_id = properties[0]["id"]
                print(f"\nTesting mortgage details for property {prop_id}...")
                
                mortgage_response = requests.get(f"{base_url}/mortgage-details/{prop_id}", headers=headers)
                if mortgage_response.status_code == 200:
                    mortgage = mortgage_response.json()
                    print(f"Mortgage details found:")
                    print(f"  Bank: {mortgage.get('bank_entity')}")
                    print(f"  Balance: {mortgage.get('outstanding_balance')}")
                    print(f"  Revisions: {len(mortgage.get('revisions', []))}")
                    
                    # Show some revision details
                    revisions = mortgage.get('revisions', [])[:5]  # First 5
                    for rev in revisions:
                        print(f"    {rev['effective_date']}: Euribor {rev.get('euribor_rate', 'N/A')}% + Margin {rev.get('margin_rate', 'N/A')}%")
                else:
                    print(f"Mortgage details request failed: {mortgage_response.status_code}")
                    print(mortgage_response.text)
        else:
            print(f"Properties request failed: {properties_response.status_code}")
            print(properties_response.text)
        
        return access_token
    else:
        print(f"Login failed: {response.status_code}")
        print(response.text)
        return None

if __name__ == "__main__":
    test_auth_and_get_token()