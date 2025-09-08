#!/usr/bin/env python3
"""
Script para sincronizar las rutas de fotos desde local a producción
"""

import sqlite3
import requests
import os
from typing import List, Dict

# URL del backend de producción
PRODUCTION_URL = "https://inmuebles-backend-api.onrender.com"

def get_local_photo_data() -> List[Dict]:
    """Obtener datos de fotos desde la base de datos local"""
    photos = []
    
    try:
        conn = sqlite3.connect('data/dev.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, address, photo FROM property WHERE photo IS NOT NULL')
        properties = cursor.fetchall()
        
        for prop in properties:
            photos.append({
                'id': prop[0],
                'address': prop[1],
                'photo_path': prop[2]
            })
            
        conn.close()
        print(f"OK Encontradas {len(photos)} propiedades con fotos en local")
        return photos
        
    except Exception as e:
        print(f"ERROR al leer base de datos local: {e}")
        return []

def update_production_photo(property_id: int, photo_path: str, token: str) -> bool:
    """Actualizar la ruta de foto en producción"""
    
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'photo': photo_path
        }
        
        response = requests.put(
            f"{PRODUCTION_URL}/properties/{property_id}",
            json=data,
            headers=headers
        )
        
        if response.status_code == 200:
            return True
        else:
            print(f"ERROR actualizando propiedad {property_id}: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"ERROR en actualizacion de propiedad {property_id}: {e}")
        return False

def login_to_production() -> str:
    """Hacer login en producción y obtener token"""
    try:
        response = requests.post(
            f"{PRODUCTION_URL}/auth/login",
            data={
                'username': 'davsanchez21277@gmail.com',
                'password': '123456'
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print("OK Login exitoso en produccion")
            return token
        else:
            print(f"ERROR en login: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"ERROR en login: {e}")
        return None

def main():
    print("=== SINCRONIZACION DE FOTOS LOCAL A PRODUCCION ===")
    print()
    
    # 1. Obtener datos locales
    local_photos = get_local_photo_data()
    if not local_photos:
        print("No hay fotos para sincronizar")
        return
    
    # 2. Login en producción
    token = login_to_production()
    if not token:
        print("No se pudo hacer login en producción")
        return
    
    # 3. Actualizar cada propiedad en producción
    print(f"Actualizando {len(local_photos)} propiedades en producción...")
    print()
    
    success_count = 0
    for photo in local_photos:
        print(f"Actualizando ID {photo['id']}: {photo['address'][:50]}...")
        print(f"  Ruta de foto: {photo['photo_path']}")
        
        if update_production_photo(photo['id'], photo['photo_path'], token):
            print(f"  OK Actualizada correctamente")
            success_count += 1
        else:
            print(f"  ERROR Fallo la actualizacion")
        print()
    
    print(f"=== RESUMEN ===")
    print(f"Total propiedades: {len(local_photos)}")
    print(f"Actualizadas exitosamente: {success_count}")
    print(f"Fallidas: {len(local_photos) - success_count}")

if __name__ == "__main__":
    main()