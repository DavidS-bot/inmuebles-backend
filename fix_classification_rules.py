#!/usr/bin/env python3

import requests
import json

# Configuration
API_BASE = "https://inmuebles-backend-api.onrender.com"
TEST_USER_EMAIL = "admin@admin.com"
TEST_USER_PASSWORD = "admin123"

def fix_classification_rules():
    """Fix classification rules by creating proper ones"""
    
    print("FIXING CLASSIFICATION RULES")
    print("=" * 50)
    
    # Step 1: Login
    print("1. Logging in as admin...")
    login_data = {
        "username": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code != 200:
            print(f"Login failed: {response.status_code}")
            return False
            
        token = response.json().get("access_token")
        print(f"Login successful")
        
    except Exception as e:
        print(f"Login error: {e}")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Step 2: Get or create a property
    print("\n2. Getting properties...")
    try:
        response = requests.get(f"{API_BASE}/properties/", headers=headers)
        
        if response.status_code == 200:
            properties = response.json()
            print(f"Found {len(properties)} properties")
            
            if len(properties) == 0:
                # Create a test property
                print("Creating test property...")
                property_data = {
                    "address": "Calle Test 123, Madrid",
                    "purchase_price": 200000,
                    "purchase_date": "2024-01-01",
                    "property_type": "apartment"
                }
                
                response = requests.post(f"{API_BASE}/properties/", headers=headers, json=property_data)
                if response.status_code == 200:
                    property_id = response.json().get('id')
                    print(f"Created property with ID: {property_id}")
                else:
                    print(f"Failed to create property: {response.text}")
                    return False
            else:
                property_id = properties[0]['id']
                print(f"Using property ID: {property_id}")
                
        else:
            print(f"Failed to get properties: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    # Step 3: Create proper classification rules
    print(f"\n3. Creating classification rules for property {property_id}...")
    
    rules_to_create = [
        {
            "property_id": property_id,
            "keyword": "alquiler",
            "category": "Renta",
            "subcategory": "Ingreso Mensual",
            "tenant_name": "Inquilino General"
        },
        {
            "property_id": property_id,
            "keyword": "hipoteca",
            "category": "Hipoteca",
            "subcategory": "Pago Mensual"
        },
        {
            "property_id": property_id,
            "keyword": "comunidad",
            "category": "Gasto",
            "subcategory": "Gastos de Comunidad"
        },
        {
            "property_id": property_id,
            "keyword": "ibi",
            "category": "Gasto",
            "subcategory": "Impuestos"
        },
        {
            "property_id": property_id,
            "keyword": "seguro",
            "category": "Gasto",
            "subcategory": "Seguros"
        }
    ]
    
    created_rules = 0
    for rule_data in rules_to_create:
        try:
            response = requests.post(f"{API_BASE}/classification-rules/", headers=headers, json=rule_data)
            
            if response.status_code == 200:
                rule = response.json()
                print(f"[OK] Created rule: {rule_data['keyword']} -> {rule_data['category']} (ID: {rule.get('id')})")
                created_rules += 1
            else:
                print(f"[ERROR] Failed to create rule {rule_data['keyword']}: {response.text}")
                
        except Exception as e:
            print(f"[ERROR] Error creating rule {rule_data['keyword']}: {e}")
    
    # Step 4: List rules to verify
    print(f"\n4. Verifying created rules...")
    try:
        response = requests.get(f"{API_BASE}/classification-rules/", headers=headers)
        
        if response.status_code == 200:
            rules = response.json()
            print(f"Total rules in database: {len(rules)}")
            
            for rule in rules:
                keyword = rule.get('keyword', 'N/A')
                category = rule.get('category', 'N/A')
                print(f"  - {keyword} -> {category}")
                
        else:
            print(f"Failed to list rules: {response.text}")
            
    except Exception as e:
        print(f"Error listing rules: {e}")
    
    print(f"\nSUMMARY: Created {created_rules} new classification rules")
    return created_rules > 0

if __name__ == "__main__":
    success = fix_classification_rules()
    if success:
        print("\n[SUCCESS] CLASSIFICATION RULES FIXED!")
        print("Check them at: https://inmuebles-web.vercel.app/financial-agent/classification-rules")
    else:
        print("\n[FAILED] FAILED TO FIX CLASSIFICATION RULES")