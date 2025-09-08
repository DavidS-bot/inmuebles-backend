#!/usr/bin/env python3
"""Clean duplicates and restore correct data in production"""

import requests
import json
import time

API = "https://inmuebles-backend-api.onrender.com"
LOCAL_API = "http://localhost:8000"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

def get_token(api_url):
    """Get auth token from API"""
    try:
        response = requests.post(
            f"{api_url}/auth/login",
            data={"username": EMAIL, "password": PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()["access_token"]
    except Exception as e:
        print(f"Login error: {e}")
    return None

def get_all_properties(api_url, token):
    """Get all properties from API"""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{api_url}/properties", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error getting properties: {e}")
    return []

def delete_all_properties(token):
    """Delete all properties in production"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get all properties
    properties = get_all_properties(API, token)
    print(f"Found {len(properties)} properties to delete")
    
    deleted = 0
    for prop in properties:
        try:
            response = requests.delete(
                f"{API}/properties/{prop['id']}", 
                headers=headers,
                timeout=10
            )
            if response.status_code in [200, 204]:
                deleted += 1
                print(f"  Deleted: {prop['address']}")
            else:
                print(f"  Failed to delete: {prop['address']} - {response.status_code}")
        except Exception as e:
            print(f"  Error deleting property {prop['id']}: {str(e)[:50]}")
        time.sleep(0.5)  # Avoid rate limiting
    
    return deleted

def upload_correct_properties(prod_token, local_properties):
    """Upload only the correct properties from local"""
    headers = {"Authorization": f"Bearer {prod_token}", "Content-Type": "application/json"}
    uploaded = 0
    
    print(f"\nUploading {len(local_properties)} properties from local...")
    
    for prop in local_properties:
        try:
            # Remove id and owner_id for creation
            prop_data = {k: v for k, v in prop.items() if k not in ["id", "owner_id"]}
            
            response = requests.post(
                f"{API}/properties", 
                json=prop_data, 
                headers=headers,
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                uploaded += 1
                print(f"  ✓ Uploaded: {prop.get('address', 'Unknown')}")
            else:
                print(f"  ✗ Failed: {prop.get('address', 'Unknown')} - {response.status_code}")
                if response.status_code == 422:
                    print(f"    Details: {response.text[:200]}")
        except Exception as e:
            print(f"  ✗ Error: {str(e)[:100]}")
        
        time.sleep(1)  # Avoid rate limiting
    
    return uploaded

def main():
    print("=" * 60)
    print("PRODUCTION DATABASE CLEANUP AND RESTORE")
    print("=" * 60)
    
    # Get tokens
    print("\n1. Authenticating...")
    local_token = get_token(LOCAL_API)
    prod_token = get_token(API)
    
    if not local_token or not prod_token:
        print("Authentication failed!")
        return
    
    print("  ✓ Authentication successful")
    
    # Get local properties (the correct ones)
    print("\n2. Getting correct properties from local...")
    local_properties = get_all_properties(LOCAL_API, local_token)
    print(f"  ✓ Found {len(local_properties)} properties in local")
    
    if len(local_properties) != 11:
        print(f"  ⚠ Warning: Expected 11 properties, found {len(local_properties)}")
        response = input("  Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Aborted")
            return
    
    # Delete all properties in production
    print("\n3. Cleaning production database...")
    deleted = delete_all_properties(prod_token)
    print(f"  ✓ Deleted {deleted} properties")
    
    # Wait a moment for database to settle
    time.sleep(2)
    
    # Upload correct properties
    print("\n4. Uploading correct properties...")
    uploaded = upload_correct_properties(prod_token, local_properties)
    
    # Verify
    print("\n5. Verifying...")
    time.sleep(2)
    prod_properties = get_all_properties(API, prod_token)
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Properties deleted: {deleted}")
    print(f"Properties uploaded: {uploaded}")
    print(f"Current properties in production: {len(prod_properties)}")
    
    if len(prod_properties) == 11:
        print("\n✓ SUCCESS! Production database has exactly 11 properties")
    else:
        print(f"\n⚠ WARNING: Production has {len(prod_properties)} properties instead of 11")
    
    print("\nCleanup completed!")

if __name__ == "__main__":
    main()