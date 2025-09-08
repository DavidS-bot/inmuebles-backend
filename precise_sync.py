#!/usr/bin/env python3
"""Precise sync with exact data"""

import requests
import json

PROD_API = "https://inmuebles-backend-api.onrender.com" 
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

# Exact properties from local
EXACT_PROPERTIES = [
    {"address": "Jose Luis Lopez de Aranguren 68, Jerez de la Frontera", "purchase_price": 115000, "property_type": "Casa"},
    {"address": "Jose Luis Lopez de Aranguren 66, Jerez de la Frontera", "purchase_price": 115000, "property_type": "Casa"},  
    {"address": "Platon 30, Jerez de la Frontera", "purchase_price": 185000, "property_type": "Casa"},
    {"address": "Jose Luis Lopez de Aranguren 22, Jerez de la Frontera", "purchase_price": 125000, "property_type": "Casa"},
    {"address": "Calle Seneca (San Isidro Guadalete), S/N, 1, B, 11594, Jerez De La Frontera", "purchase_price": 145000, "property_type": "Piso"},
    {"address": "Lago de Enol, bloque 1, planta primera, puerta F, 11406, Jerez De La Frontera", "purchase_price": 80000, "property_type": "Piso"},
    {"address": "Lago de Enol, bloque 1, planta segunda, puerta A, 11406, Jerez De La Frontera", "purchase_price": 90000, "property_type": "Piso"},
    {"address": "Lago de Enol, bloque 1, planta segunda, puerta B, 11406, Jerez De La Frontera", "purchase_price": 80000, "property_type": "Piso"},
    {"address": "Lago de Bañolas, nº 1, puerta 4, 11406, Jerez De La Frontera", "purchase_price": 50000, "property_type": "Piso"},
    {"address": "Lago de Bañolas, nº 1, puerta 9, 11406, Jerez De La Frontera", "purchase_price": 50000, "property_type": "Piso"},
    {"address": "Lago de Enol, sin número, puerta G, 11406, Jerez De La Frontera", "purchase_price": 75500, "property_type": "Piso"}
]

def login():
    r = requests.post(f"{PROD_API}/auth/login", data={"username": EMAIL, "password": PASSWORD})
    return r.json()["access_token"] if r.status_code == 200 else None

def clear_and_upload():
    token = login()
    if not token:
        print("Login failed")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get current properties
    current = requests.get(f"{PROD_API}/properties", headers=headers).json()
    print(f"Current: {len(current)} properties")
    
    # Delete all current
    for prop in current:
        requests.delete(f"{PROD_API}/properties/{prop['id']}", headers=headers)
    
    print("Deleted all properties")
    
    # Upload exact 11
    uploaded = 0
    for prop in EXACT_PROPERTIES:
        r = requests.post(f"{PROD_API}/properties", json=prop, headers=headers)
        if r.status_code in [200, 201]:
            uploaded += 1
            print(f"OK: {prop['address'][:40]}")
        else:
            print(f"FAIL: {prop['address'][:40]} - {r.status_code}")
    
    print(f"Uploaded: {uploaded}/11")
    
    # Verify
    final = requests.get(f"{PROD_API}/properties", headers=headers).json()
    print(f"Final count: {len(final)}")

if __name__ == "__main__":
    clear_and_upload()