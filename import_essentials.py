#!/usr/bin/env python3
"""Script para importar datos esenciales (hipotecas y reglas)"""

import json
import requests

BACKEND_URL = "https://inmuebles-backend-api.onrender.com"
USER_EMAIL = "davsanchez21277@gmail.com"
USER_PASSWORD = "123456"

def get_auth_token():
    login_data = {"username": USER_EMAIL, "password": USER_PASSWORD}
    response = requests.post(f"{BACKEND_URL}/auth/login", data=login_data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    return response.json()["access_token"] if response.status_code == 200 else None

def get_production_properties(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BACKEND_URL}/properties", headers=headers)
    return response.json() if response.status_code == 200 else []

def create_property_mapping(local_properties, production_properties):
    mapping = {}
    for local_prop in local_properties:
        local_address = local_prop.get('address', '').strip().lower()
        local_id = local_prop.get('id')
        for prod_prop in production_properties:
            prod_address = prod_prop.get('address', '').strip().lower()
            if local_address == prod_address:
                mapping[local_id] = prod_prop.get('id')
                break
    return mapping

def import_mortgages(token, mortgages_data, property_mapping):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    imported = 0
    
    for mortgage in mortgages_data:
        local_property_id = mortgage.get('property_id')
        if local_property_id not in property_mapping:
            continue
            
        mortgage_data = {k: v for k, v in mortgage.items() if k != 'id'}
        mortgage_data['property_id'] = property_mapping[local_property_id]
        
        response = requests.post(f"{BACKEND_URL}/mortgage-details", json=mortgage_data, headers=headers)
        if response.status_code in [200, 201]:
            imported += 1
            print(f"Mortgage imported for property {local_property_id}")
    
    return imported

def import_rules(token, rules_data):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    imported = 0
    
    for rule in rules_data:
        rule_data = {k: v for k, v in rule.items() if k != 'id'}
        response = requests.post(f"{BACKEND_URL}/classification-rules", json=rule_data, headers=headers)
        if response.status_code in [200, 201]:
            imported += 1
            print(f"Rule imported: {rule_data.get('name', 'N/A')}")
    
    return imported

def main():
    with open("exported_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    token = get_auth_token()
    production_properties = get_production_properties(token)
    property_mapping = create_property_mapping(data["properties"], production_properties)
    
    print(f"Importing {len(data['mortgages'])} mortgages...")
    mortgages_imported = import_mortgages(token, data["mortgages"], property_mapping)
    
    print(f"\nImporting {len(data['classification_rules'])} rules...")
    rules_imported = import_rules(token, data["classification_rules"])
    
    print(f"\nSUMMARY:")
    print(f"Mortgages: {mortgages_imported}/{len(data['mortgages'])}")
    print(f"Rules: {rules_imported}/{len(data['classification_rules'])}")

if __name__ == "__main__":
    main()