#!/usr/bin/env python3
"""Script para importar TODOS los datos al backend de producción"""

import json
import requests
import sys
from datetime import datetime

# Configuración
BACKEND_URL = "https://inmuebles-backend-api.onrender.com"
USER_EMAIL = "davsanchez21277@gmail.com"
USER_PASSWORD = "123456"

def get_auth_token():
    """Obtener token de autenticación"""
    login_data = {
        "username": USER_EMAIL,
        "password": USER_PASSWORD
    }
    
    response = requests.post(
        f"{BACKEND_URL}/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("Authentication successful")
        return token
    else:
        print(f"Authentication failed: {response.status_code}")
        return None

def get_production_properties(token):
    """Obtener propiedades de producción para mapear IDs"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BACKEND_URL}/properties", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    return []

def import_mortgages(token, mortgages_data, property_mapping):
    """Importar hipotecas"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    imported = 0
    
    print(f"\nImporting {len(mortgages_data)} mortgages...")
    
    for mortgage in mortgages_data:
        # Mapear property_id local al ID de producción
        local_property_id = mortgage.get('property_id')
        if local_property_id not in property_mapping:
            print(f"Skipping mortgage: property {local_property_id} not found")
            continue
            
        mortgage_data = {k: v for k, v in mortgage.items() if k != 'id'}
        mortgage_data['property_id'] = property_mapping[local_property_id]
        
        response = requests.post(
            f"{BACKEND_URL}/mortgage-details",
            json=mortgage_data,
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            imported += 1
            print(f"Mortgage imported for property {local_property_id}")
        else:
            print(f"Failed to import mortgage: {response.status_code} - {response.text}")
    
    print(f"Imported {imported}/{len(mortgages_data)} mortgages")
    return imported

def import_financial_movements(token, movements_data, property_mapping):
    """Importar movimientos financieros"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    imported = 0
    
    print(f"\nImporting {len(movements_data)} financial movements...")
    
    for movement in movements_data:
        movement_data = {k: v for k, v in movement.items() if k != 'id'}
        
        # Mapear property_id si existe
        if 'property_id' in movement_data and movement_data['property_id']:
            local_property_id = movement_data['property_id']
            if local_property_id in property_mapping:
                movement_data['property_id'] = property_mapping[local_property_id]
            else:
                movement_data['property_id'] = None
        
        response = requests.post(
            f"{BACKEND_URL}/financial-movements",
            json=movement_data,
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            imported += 1
            if imported % 100 == 0:  # Progress every 100 movements
                print(f"Imported {imported} movements...")
        else:
            print(f"Failed to import movement: {response.status_code}")
    
    print(f"Imported {imported}/{len(movements_data)} financial movements")
    return imported

def import_classification_rules(token, rules_data):
    """Importar reglas de clasificación"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    imported = 0
    
    print(f"\nImporting {len(rules_data)} classification rules...")
    
    for rule in rules_data:
        rule_data = {k: v for k, v in rule.items() if k != 'id'}
        
        response = requests.post(
            f"{BACKEND_URL}/classification-rules",
            json=rule_data,
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            imported += 1
            print(f"Rule imported: {rule_data.get('name', 'N/A')}")
        else:
            print(f"Failed to import rule: {response.status_code} - {response.text}")
    
    print(f"Imported {imported}/{len(rules_data)} classification rules")
    return imported

def create_property_mapping(local_properties, production_properties):
    """Crear mapeo entre IDs locales y de producción basado en direcciones"""
    mapping = {}
    
    for local_prop in local_properties:
        local_address = local_prop.get('address', '').strip().lower()
        local_id = local_prop.get('id')
        
        for prod_prop in production_properties:
            prod_address = prod_prop.get('address', '').strip().lower()
            prod_id = prod_prop.get('id')
            
            if local_address == prod_address:
                mapping[local_id] = prod_id
                break
    
    print(f"Property mapping created: {len(mapping)} matches")
    return mapping

def import_all_data():
    """Importar todos los datos"""
    # Cargar datos exportados
    try:
        with open("exported_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("exported_data.json not found. Run export_data.py first")
        return False
    
    print(f"Loaded data:")
    print(f"  - {len(data['properties'])} properties")
    print(f"  - {len(data['mortgages'])} mortgages")
    print(f"  - {len(data['financial_movements'])} financial movements")
    print(f"  - {len(data['classification_rules'])} classification rules")
    
    # Obtener token de autenticación
    token = get_auth_token()
    if not token:
        return False
    
    # Obtener propiedades de producción para mapear IDs
    production_properties = get_production_properties(token)
    print(f"Found {len(production_properties)} properties in production")
    
    # Crear mapeo de IDs
    property_mapping = create_property_mapping(data["properties"], production_properties)
    
    # Importar hipotecas
    mortgages_imported = import_mortgages(token, data["mortgages"], property_mapping)
    
    # Importar reglas de clasificación
    rules_imported = import_classification_rules(token, data["classification_rules"])
    
    # Importar movimientos financieros (puede tardar más)
    print("\nImporting financial movements (this may take a while)...")
    movements_imported = import_financial_movements(token, data["financial_movements"], property_mapping)
    
    # Resumen
    print(f"\n=== IMPORT SUMMARY ===")
    print(f"Properties: 11 (already imported)")
    print(f"Mortgages: {mortgages_imported}/{len(data['mortgages'])}")
    print(f"Financial Movements: {movements_imported}/{len(data['financial_movements'])}")
    print(f"Classification Rules: {rules_imported}/{len(data['classification_rules'])}")
    
    return True

if __name__ == "__main__":
    print("Starting complete data import to production backend...")
    success = import_all_data()
    if success:
        print("\nComplete import finished!")
        print("Check your web application - all data should now be available!")
    else:
        print("\nImport failed")