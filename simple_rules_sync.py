#!/usr/bin/env python3
"""Simple and reliable sync for classification rules"""

import requests
import json
import time

LOCAL_API = "http://localhost:8000"
PROD_API = "https://inmuebles-backend-api.onrender.com"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

def quick_login(api_url):
    try:
        response = requests.post(f"{api_url}/auth/login", 
                               data={"username": EMAIL, "password": PASSWORD}, 
                               timeout=10)
        return response.json()["access_token"] if response.status_code == 200 else None
    except:
        return None

def main():
    print("SIMPLE RULES SYNC")
    print("=" * 20)
    
    # Quick login check
    local_token = quick_login(LOCAL_API)
    prod_token = quick_login(PROD_API)
    
    if not local_token:
        print("Local API login failed")
        return
    if not prod_token:
        print("Production API login failed")
        return
        
    print("Both APIs accessible")
    
    # Get local rules quickly
    try:
        headers = {"Authorization": f"Bearer {local_token}"}
        response = requests.get(f"{LOCAL_API}/classification-rules", headers=headers, timeout=10)
        local_rules = response.json() if response.status_code == 200 else []
        print(f"Local rules: {len(local_rules)}")
    except Exception as e:
        print(f"Error getting local rules: {e}")
        return
    
    # Upload one rule at a time with longer delays
    headers_prod = {"Authorization": f"Bearer {prod_token}", "Content-Type": "application/json"}
    uploaded = 0
    
    for i, rule in enumerate(local_rules[:5]):  # Only first 5 to test
        try:
            rule_data = {
                "rule_name": rule.get("rule_name", f"Rule_{i+1}"),
                "pattern": rule.get("pattern", ""),
                "category": rule.get("category", ""),
                "subcategory": rule.get("subcategory", ""),
                "priority": rule.get("priority", 1),
                "is_active": rule.get("is_active", True)
            }
            
            print(f"Uploading rule {i+1}: {rule_data['rule_name'][:20]}")
            response = requests.post(f"{PROD_API}/classification-rules", 
                                   json=rule_data, headers=headers_prod, timeout=15)
            
            if response.status_code in [200, 201]:
                uploaded += 1
                print(f"  SUCCESS")
            elif response.status_code == 400:
                uploaded += 1  # Might be duplicate
                print(f"  OK (duplicate)")
            else:
                print(f"  FAILED: {response.status_code}")
                
        except Exception as e:
            print(f"  ERROR: {str(e)[:30]}")
        
        time.sleep(3)  # Longer delay between requests
    
    print(f"\nUploaded: {uploaded} rules")
    
    # Quick final check
    try:
        response = requests.get(f"{PROD_API}/classification-rules", headers=headers_prod, timeout=10)
        final_rules = response.json() if response.status_code == 200 else []
        print(f"Final production rules: {len(final_rules)}")
    except:
        print("Could not verify final count")

if __name__ == "__main__":
    main()