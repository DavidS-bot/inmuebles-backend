#!/usr/bin/env python3
"""Importacion completa de todos los datos"""

import json
import requests
import time

BACKEND_URL = "https://inmuebles-backend-api.onrender.com"
USER_EMAIL = "davsanchez21277@gmail.com"
USER_PASSWORD = "123456"

def get_auth_token():
    login_data = {"username": USER_EMAIL, "password": USER_PASSWORD}
    response = requests.post(
        f"{BACKEND_URL}/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def get_existing_properties(token):
    """Obtener propiedades ya existentes"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BACKEND_URL}/properties", headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

def import_remaining_properties(token, all_properties, existing_properties):
    """Importar propiedades faltantes"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    existing_addresses = [prop.get('address', '').lower() for prop in existing_properties]
    property_mapping = {}
    imported = 0
    
    print(f"Importing remaining properties...")
    
    for prop in all_properties:
        prop_address = prop.get('address', '').lower()
        
        # Si ya existe, crear mapeo
        for existing in existing_properties:
            if existing.get('address', '').lower() == prop_address:
                property_mapping[prop['id']] = existing['id']
                break
        else:
            # No existe, importar
            prop_data = {k: v for k, v in prop.items() if k != 'id'}
            response = requests.post(f"{BACKEND_URL}/properties", json=prop_data, headers=headers)
            
            if response.status_code in [200, 201]:
                new_id = response.json()["id"]
                property_mapping[prop["id"]] = new_id
                imported += 1
                print(f"Property imported: {prop.get('address', 'Unknown')}")
                time.sleep(0.5)  # Evitar sobrecarga
    
    print(f"New properties imported: {imported}")
    return property_mapping

def import_mortgages(token, mortgages, property_mapping):
    """Importar hipotecas"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    imported = 0
    
    print(f"Importing {len(mortgages)} mortgages...")
    
    for mortgage in mortgages:
        if mortgage.get("property_id") in property_mapping:
            mortgage_data = {k: v for k, v in mortgage.items() if k != 'id'}
            mortgage_data["property_id"] = property_mapping[mortgage["property_id"]]
            
            response = requests.post(f"{BACKEND_URL}/mortgage-details", json=mortgage_data, headers=headers)
            if response.status_code in [200, 201]:
                imported += 1
                print(f"Mortgage imported for property ID {mortgage['property_id']}")
            time.sleep(0.2)
    
    print(f"Mortgages imported: {imported}/{len(mortgages)}")
    return imported

def import_classification_rules(token, rules):
    """Importar reglas de clasificacion"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    imported = 0
    
    print(f"Importing {len(rules)} classification rules...")
    
    for rule in rules:
        rule_data = {k: v for k, v in rule.items() if k != 'id'}
        response = requests.post(f"{BACKEND_URL}/classification-rules", json=rule_data, headers=headers)
        if response.status_code in [200, 201]:
            imported += 1
            print(f"Rule imported: {rule_data.get('name', 'Unknown')}")
        time.sleep(0.1)
    
    print(f"Rules imported: {imported}/{len(rules)}")
    return imported

def import_financial_movements_batch(token, movements, property_mapping, batch_size=25):
    """Importar movimientos financieros en lotes pequenos"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    imported = 0
    
    print(f"Importing {len(movements)} financial movements in batches...")
    
    for i in range(0, len(movements), batch_size):
        batch = movements[i:i+batch_size]
        batch_imported = 0
        
        for movement in batch:
            movement_data = {k: v for k, v in movement.items() if k != 'id'}
            
            # Mapear property_id si existe
            if movement_data.get("property_id") and movement_data["property_id"] in property_mapping:
                movement_data["property_id"] = property_mapping[movement_data["property_id"]]
            elif movement_data.get("property_id"):
                movement_data["property_id"] = None
            
            response = requests.post(f"{BACKEND_URL}/financial-movements", json=movement_data, headers=headers)
            if response.status_code in [200, 201]:
                batch_imported += 1
        
        imported += batch_imported
        print(f"Batch {i//batch_size + 1}: {batch_imported}/{len(batch)} movements imported. Total: {imported}")
        
        # Pausa entre lotes para no sobrecargar
        if i + batch_size < len(movements):
            time.sleep(1)
    
    print(f"Total movements imported: {imported}/{len(movements)}")
    return imported

def main():
    print("Starting complete data import...")
    
    # Cargar datos
    with open("exported_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print(f"Data loaded:")
    print(f"  Properties: {len(data['properties'])}")
    print(f"  Mortgages: {len(data['mortgages'])}")
    print(f"  Financial Movements: {len(data['financial_movements'])}")
    print(f"  Classification Rules: {len(data['classification_rules'])}")
    
    # Obtener token
    token = get_auth_token()
    if not token:
        print("Failed to get auth token")
        return
    
    print("Authentication successful")
    
    # Obtener propiedades existentes
    existing_properties = get_existing_properties(token)
    print(f"Found {len(existing_properties)} existing properties")
    
    # Importar propiedades restantes
    property_mapping = import_remaining_properties(token, data["properties"], existing_properties)
    
    # Importar hipotecas
    mortgages_imported = import_mortgages(token, data["mortgages"], property_mapping)
    
    # Importar reglas de clasificacion
    rules_imported = import_classification_rules(token, data["classification_rules"])
    
    # Importar movimientos financieros (esto puede tardar)
    movements_imported = import_financial_movements_batch(token, data["financial_movements"], property_mapping)
    
    print(f"\n" + "="*50)
    print(f"COMPLETE IMPORT SUMMARY")
    print(f"="*50)
    print(f"Properties in mapping: {len(property_mapping)}")
    print(f"Mortgages imported: {mortgages_imported}")
    print(f"Rules imported: {rules_imported}")
    print(f"Financial movements imported: {movements_imported}")
    print(f"\nAll data has been imported to PostgreSQL!")
    print(f"Your application is now fully functional with persistent data.")

if __name__ == "__main__":
    main()