#!/usr/bin/env python3
"""Migrar todos los datos a PostgreSQL en producción"""

import json
import requests
import time

BACKEND_URL = "https://inmuebles-backend-api.onrender.com"
USER_EMAIL = "davsanchez21277@gmail.com"
USER_PASSWORD = "123456"

def wait_for_backend():
    """Esperar a que el backend esté listo con PostgreSQL"""
    print("Waiting for backend to be ready with PostgreSQL...")
    for i in range(30):
        try:
            response = requests.get(f"{BACKEND_URL}/docs", timeout=5)
            if response.status_code == 200:
                print("Backend is ready!")
                return True
        except:
            pass
        print(f"Waiting... ({i+1}/30)")
        time.sleep(10)
    return False

def register_user():
    """Registrar usuario"""
    data = {"email": USER_EMAIL, "password": USER_PASSWORD}
    response = requests.post(f"{BACKEND_URL}/auth/register", json=data)
    if response.status_code in [200, 201]:
        print(f"User registered: {USER_EMAIL}")
        return True
    elif response.status_code == 400:
        print("User already exists")
        return True
    else:
        print(f"Failed to register user: {response.text}")
        return False

def get_auth_token():
    """Obtener token"""
    data = {"username": USER_EMAIL, "password": USER_PASSWORD}
    response = requests.post(
        f"{BACKEND_URL}/auth/login",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def import_properties(token, properties):
    """Importar propiedades"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    imported = 0
    property_mapping = {}
    
    for prop in properties:
        prop_data = {k: v for k, v in prop.items() if k != 'id'}
        response = requests.post(f"{BACKEND_URL}/properties", json=prop_data, headers=headers)
        
        if response.status_code in [200, 201]:
            new_id = response.json()["id"]
            property_mapping[prop["id"]] = new_id
            imported += 1
            print(f"Property imported: {prop.get('address', 'N/A')}")
    
    return imported, property_mapping

def import_mortgages(token, mortgages, property_mapping):
    """Importar hipotecas"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    imported = 0
    
    for mortgage in mortgages:
        if mortgage.get("property_id") in property_mapping:
            mortgage_data = {k: v for k, v in mortgage.items() if k != 'id'}
            mortgage_data["property_id"] = property_mapping[mortgage["property_id"]]
            
            response = requests.post(f"{BACKEND_URL}/mortgage-details", json=mortgage_data, headers=headers)
            if response.status_code in [200, 201]:
                imported += 1
    
    print(f"Imported {imported}/{len(mortgages)} mortgages")
    return imported

def import_rules(token, rules):
    """Importar reglas"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    imported = 0
    
    for rule in rules:
        rule_data = {k: v for k, v in rule.items() if k != 'id'}
        response = requests.post(f"{BACKEND_URL}/classification-rules", json=rule_data, headers=headers)
        if response.status_code in [200, 201]:
            imported += 1
    
    print(f"Imported {imported}/{len(rules)} rules")
    return imported

def import_movements_batch(token, movements, property_mapping, batch_size=50):
    """Importar movimientos en lotes"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    imported = 0
    
    for i in range(0, len(movements), batch_size):
        batch = movements[i:i+batch_size]
        for movement in batch:
            movement_data = {k: v for k, v in movement.items() if k != 'id'}
            
            if movement_data.get("property_id") and movement_data["property_id"] in property_mapping:
                movement_data["property_id"] = property_mapping[movement_data["property_id"]]
            
            response = requests.post(f"{BACKEND_URL}/financial-movements", json=movement_data, headers=headers)
            if response.status_code in [200, 201]:
                imported += 1
        
        print(f"Imported {imported}/{len(movements)} movements...")
    
    return imported

def main():
    # Cargar datos
    with open("exported_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print(f"Data to import:")
    print(f"  - {len(data['properties'])} properties")
    print(f"  - {len(data['mortgages'])} mortgages")
    print(f"  - {len(data['financial_movements'])} movements")
    print(f"  - {len(data['classification_rules'])} rules")
    
    # Esperar a que el backend esté listo
    if not wait_for_backend():
        print("Backend not ready after 5 minutes")
        return
    
    # Registrar usuario
    if not register_user():
        return
    
    # Obtener token
    token = get_auth_token()
    if not token:
        print("Failed to get auth token")
        return
    
    print("\nStarting import to PostgreSQL...")
    
    # Importar propiedades
    props_imported, property_mapping = import_properties(token, data["properties"])
    print(f"Properties: {props_imported}/{len(data['properties'])}")
    
    # Importar hipotecas
    mortgages_imported = import_mortgages(token, data["mortgages"], property_mapping)
    
    # Importar reglas
    rules_imported = import_rules(token, data["classification_rules"])
    
    # Importar movimientos
    print("\nImporting movements (this will take a while)...")
    movements_imported = import_movements_batch(token, data["financial_movements"], property_mapping)
    
    print(f"\n=== IMPORT COMPLETE ===")
    print(f"Properties: {props_imported}")
    print(f"Mortgages: {mortgages_imported}")
    print(f"Rules: {rules_imported}")
    print(f"Movements: {movements_imported}")
    print("\nAll data migrated to PostgreSQL!")

if __name__ == "__main__":
    main()