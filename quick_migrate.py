#!/usr/bin/env python3
"""Migración rápida de datos esenciales"""

import json
import requests

BACKEND_URL = "https://inmuebles-backend-api.onrender.com"
USER_EMAIL = "davsanchez21277@gmail.com"
USER_PASSWORD = "123456"

def main():
    print("Quick migration to PostgreSQL...")
    
    # Cargar datos
    with open("exported_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Registrar usuario
    print("Registering user...")
    user_data = {"email": USER_EMAIL, "password": USER_PASSWORD}
    response = requests.post(f"{BACKEND_URL}/auth/register", json=user_data)
    if response.status_code in [200, 201]:
        print("User registered successfully")
    else:
        print(f"User registration: {response.status_code}")
    
    # Login
    login_data = {"username": USER_EMAIL, "password": USER_PASSWORD}
    response = requests.post(
        f"{BACKEND_URL}/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code != 200:
        print("Failed to login")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Importar propiedades
    print(f"Importing {len(data['properties'])} properties...")
    property_mapping = {}
    props_imported = 0
    
    for prop in data["properties"]:
        prop_data = {k: v for k, v in prop.items() if k != 'id'}
        response = requests.post(f"{BACKEND_URL}/properties", json=prop_data, headers=headers)
        
        if response.status_code in [200, 201]:
            new_id = response.json()["id"]
            property_mapping[prop["id"]] = new_id
            props_imported += 1
            print(f"  ✓ {prop.get('address', 'N/A')}")
    
    print(f"Properties imported: {props_imported}/{len(data['properties'])}")
    
    # Importar algunas reglas importantes
    print(f"\nImporting {len(data['classification_rules'])} rules...")
    rules_imported = 0
    
    for rule in data["classification_rules"][:10]:  # Solo las primeras 10
        rule_data = {k: v for k, v in rule.items() if k != 'id'}
        response = requests.post(f"{BACKEND_URL}/classification-rules", json=rule_data, headers=headers)
        if response.status_code in [200, 201]:
            rules_imported += 1
    
    print(f"Rules imported: {rules_imported}")
    
    print(f"\n=== QUICK MIGRATION COMPLETE ===")
    print(f"✓ User: {USER_EMAIL}")
    print(f"✓ Properties: {props_imported}")
    print(f"✓ Rules: {rules_imported}")
    print("\nYour app should now work with PostgreSQL!")
    print("You can import movements later when the server is less busy.")

if __name__ == "__main__":
    main()