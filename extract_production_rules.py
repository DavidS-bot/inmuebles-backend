#!/usr/bin/env python3
"""
Script to extract classification rules from production API
"""
import requests
import json
import os
from typing import List, Dict

# Production API configuration
PROD_API = "https://inmuebles-backend-api.onrender.com"
FRONTEND_URL = "https://inmuebles-david.vercel.app"

# You need to provide these credentials
EMAIL = "davsanchez21277@gmail.com"  # Replace with actual email
PASSWORD = "123456"  # Known working password from production setup

def get_auth_token(email: str, password: str) -> str:
    """Authenticate with production API and get token"""
    login_data = {
        "username": email,
        "password": password
    }
    
    try:
        response = requests.post(
            f"{PROD_API}/auth/login", 
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30
        )
        
        if response.status_code == 200:
            token_data = response.json()
            return token_data["access_token"]
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Login error: {e}")
        return None

def get_classification_rules(token: str) -> List[Dict]:
    """Get all classification rules from production API"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{PROD_API}/classification-rules/",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get rules: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        print(f"Error getting rules: {e}")
        return []

def get_properties(token: str) -> List[Dict]:
    """Get all properties to map property_id to address"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{PROD_API}/properties/",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get properties: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Error getting properties: {e}")
        return []

def format_rules_for_import(rules: List[Dict], properties: List[Dict]) -> List[Dict]:
    """Format rules for easy import to local database"""
    # Create property mapping
    property_map = {prop['id']: prop for prop in properties}
    
    formatted_rules = []
    
    for rule in rules:
        formatted_rule = {
            "id": rule["id"],
            "property_id": rule["property_id"],
            "property_address": property_map.get(rule["property_id"], {}).get("address", "Unknown"),
            "keyword": rule["keyword"],
            "category": rule["category"],
            "subcategory": rule.get("subcategory"),
            "tenant_name": rule.get("tenant_name"),
            "is_active": rule.get("is_active", True)
        }
        formatted_rules.append(formatted_rule)
    
    return formatted_rules

def main():
    print("EXTRACTING CLASSIFICATION RULES FROM PRODUCTION")
    print("=" * 60)
    
    # Use known working credentials
    password = PASSWORD
    
    # Step 1: Authenticate
    print("\n1. Authenticating with production API...")
    token = get_auth_token(EMAIL, password)
    
    if not token:
        print("Authentication failed")
        return
    
    print("Authentication successful")
    
    # Step 2: Get properties for mapping
    print("\n2. Getting properties for reference...")
    properties = get_properties(token)
    print(f"Found {len(properties)} properties")
    
    # Step 3: Get classification rules
    print("\n3. Getting classification rules...")
    rules = get_classification_rules(token)
    print(f"Found {len(rules)} classification rules")
    
    if not rules:
        print("No rules found or error occurred")
        return
    
    # Step 4: Format rules
    print("\n4. Formatting rules for import...")
    formatted_rules = format_rules_for_import(rules, properties)
    
    # Step 5: Save to file
    output_file = "production_classification_rules.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(formatted_rules, f, indent=2, ensure_ascii=False)
    
    print(f"Rules saved to {output_file}")
    
    # Step 6: Generate summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    categories = {}
    properties_with_rules = set()
    
    for rule in formatted_rules:
        category = rule["category"]
        categories[category] = categories.get(category, 0) + 1
        properties_with_rules.add(rule["property_id"])
    
    print(f"Total rules extracted: {len(formatted_rules)}")
    print(f"Properties with rules: {len(properties_with_rules)}")
    print("\nRules by category:")
    for category, count in categories.items():
        print(f"  {category}: {count}")
    
    print(f"\nDetailed rules saved to: {output_file}")
    print("\nSample rules:")
    for i, rule in enumerate(formatted_rules[:5]):
        print(f"{i+1}. {rule['keyword']} → {rule['category']}" + 
              (f" ({rule['subcategory']})" if rule['subcategory'] else "") + 
              f" [Property: {rule['property_address']}]")
    
    if len(formatted_rules) > 5:
        print(f"... and {len(formatted_rules) - 5} more rules")

if __name__ == "__main__":
    main()