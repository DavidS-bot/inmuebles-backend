#!/usr/bin/env python3
"""Script para importar datos al backend de producción"""

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
        print(response.text)
        return None

def import_properties(token, properties_data):
    """Importar propiedades"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    imported = 0
    
    for prop in properties_data:
        # Remover el ID para que el backend asigne uno nuevo
        prop_data = {k: v for k, v in prop.items() if k != 'id'}
        
        response = requests.post(
            f"{BACKEND_URL}/properties",
            json=prop_data,
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            imported += 1
            print(f"Property imported: {prop_data.get('address', 'N/A')}")
        else:
            print(f"Failed to import property: {response.status_code}")
            print(f"   Data: {prop_data.get('address', 'N/A')}")
            print(f"   Error: {response.text}")
    
    print(f"Imported {imported}/{len(properties_data)} properties")
    return imported

def import_data():
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
    
    # Importar propiedades (empezamos por esto)
    print("\nImporting properties...")
    imported_properties = import_properties(token, data["properties"])
    
    if imported_properties > 0:
        print(f"\nSuccessfully imported {imported_properties} properties!")
        print("You can now see your properties in the web application")
        print("Mortgages, movements and rules can be imported next if needed")
    else:
        print("No properties were imported")
    
    return imported_properties > 0

if __name__ == "__main__":
    print("Starting data import to production backend...")
    success = import_data()
    if success:
        print("\nImport completed successfully!")
    else:
        print("\nImport failed")