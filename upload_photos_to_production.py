#!/usr/bin/env python3
"""
Script para subir fotos físicas al servidor de producción
"""

import os
import requests
from pathlib import Path

# URL del backend de producción
PRODUCTION_URL = "https://inmuebles-backend-api.onrender.com"

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

def upload_photo(file_path: str, token: str) -> bool:
    """Subir una foto individual al servidor"""
    
    try:
        headers = {
            'Authorization': f'Bearer {token}',
        }
        
        filename = os.path.basename(file_path)
        
        with open(file_path, 'rb') as f:
            files = {'file': (filename, f, 'image/jpeg')}
            
            response = requests.post(
                f"{PRODUCTION_URL}/uploads/photo",
                files=files,
                headers=headers
            )
        
        if response.status_code == 200:
            print(f"  OK Subida exitosa: {filename}")
            return True
        else:
            print(f"  ERROR {response.status_code}: {filename}")
            return False
            
    except Exception as e:
        print(f"  ERROR subiendo {filename}: {e}")
        return False

def main():
    print("=== SUBIDA DE FOTOS AL SERVIDOR DE PRODUCCION ===")
    print()
    
    # 1. Login en producción
    token = login_to_production()
    if not token:
        print("No se pudo hacer login en producción")
        return
    
    # 2. Obtener lista de fotos a subir
    uploads_dir = Path("uploads")
    if not uploads_dir.exists():
        print("ERROR: Directorio uploads no encontrado")
        return
    
    # Obtener todas las imágenes
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    photos = []
    
    for file_path in uploads_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            photos.append(str(file_path))
    
    if not photos:
        print("No se encontraron fotos para subir")
        return
    
    print(f"Encontradas {len(photos)} fotos para subir")
    print()
    
    # 3. Subir cada foto
    success_count = 0
    
    for i, photo_path in enumerate(photos, 1):
        filename = os.path.basename(photo_path)
        size_kb = os.path.getsize(photo_path) / 1024
        
        print(f"[{i}/{len(photos)}] Subiendo {filename} ({size_kb:.1f} KB)...")
        
        if upload_photo(photo_path, token):
            success_count += 1
        
        print()
    
    print("=== RESUMEN ===")
    print(f"Total fotos: {len(photos)}")
    print(f"Subidas exitosamente: {success_count}")
    print(f"Fallidas: {len(photos) - success_count}")

if __name__ == "__main__":
    main()