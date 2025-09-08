#!/usr/bin/env python3
"""
Subir movimientos de Bankinter al backend
"""

import pandas as pd
import requests
from datetime import datetime
import json

def upload_bankinter_movements():
    """Subir movimientos del CSV de Bankinter al backend"""
    
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    # Login al backend
    print("[LOGIN] Haciendo login...")
    login_data = {
        "username": "davsanchez21277@gmail.com", 
        "password": "123456"
    }
    
    response = requests.post(
        f"{backend_url}/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code != 200:
        print(f"[ERROR] Error en login: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[SUCCESS] Login exitoso")
    
    # Leer el CSV con movimientos reales
    csv_file = "bankinter_movimientos_20250823_103002.csv"
    print(f"[CSV] Leyendo {csv_file}...")
    
    try:
        df = pd.read_csv(csv_file)
        print(f"[CSV] CSV leido: {len(df)} filas")
        
        # Filtrar solo movimientos reales (excluir saldos)
        df_movements = df[~df['Categoria'].isin(['Saldo'])].copy()
        print(f"[MOVEMENTS] Movimientos financieros: {len(df_movements)}")
        
        # Contadores
        uploaded = 0
        duplicates = 0
        errors = 0
        
        # Subir cada movimiento
        for index, row in df_movements.iterrows():
            try:
                # Convertir fecha al formato correcto (cambiar 2025 a 2024)
                fecha_str = row['Fecha']
                fecha_dt = datetime.strptime(fecha_str, '%d/%m/%Y')
                # Fix future dates - change 2025 to 2024
                if fecha_dt.year == 2025:
                    fecha_dt = fecha_dt.replace(year=2024)
                fecha_iso = fecha_dt.strftime('%Y-%m-%d')
                
                # Preparar el movimiento 
                movement_data = {
                    "date": fecha_iso,
                    "concept": str(row['Concepto']),
                    "amount": float(row['Importe']),
                    "category": "Sin clasificar",  # Se clasificará automáticamente con las reglas
                    "property_id": 1  # Usar property ID que sabemos que existe
                }
                
                # Intentar subir
                response = requests.post(
                    f"{backend_url}/financial-movements/",
                    json=movement_data,
                    headers=headers
                )
                
                if response.status_code == 201:
                    uploaded += 1
                    print(f"[OK] {uploaded:2d}. {fecha_str} | {row['Concepto'][:40]} | {row['Importe']} EUR")
                elif response.status_code == 400 and "already exists" in response.text.lower():
                    duplicates += 1
                    print(f"[DUP] {duplicates:2d}. Duplicado: {fecha_str} | {row['Concepto'][:40]}")
                else:
                    errors += 1
                    print(f"[ERR] Error {response.status_code}: {row['Concepto'][:40]} - {response.text[:100]}")
                    
            except Exception as e:
                errors += 1
                print(f"[ERR] Error procesando fila {index}: {e}")
                
        # Resumen final
        print("\\n" + "="*60)
        print("[RESUMEN] RESUMEN DE IMPORTACION:")
        print("="*60)
        print(f"[SUCCESS] Movimientos subidos: {uploaded}")
        print(f"[DUP] Duplicados omitidos: {duplicates}")  
        print(f"[ERROR] Errores: {errors}")
        print(f"[TOTAL] Total procesados: {uploaded + duplicates + errors}")
        
        if uploaded > 0:
            print(f"\\n[SUCCESS] Importacion exitosa! {uploaded} nuevos movimientos agregados.")
            print("\\n[NEXT] Proximos pasos:")
            print("1. Ve a https://inmuebles-david.vercel.app/financial-agent/movements")
            print("2. Verifica que aparezcan los nuevos movimientos")
            print("3. Las reglas de clasificacion se aplicaran automaticamente")
        else:
            print("\\n[WARNING] No se importaron movimientos nuevos (posiblemente duplicados)")
            
    except Exception as e:
        print(f"[ERROR] Error leyendo CSV: {e}")

if __name__ == "__main__":
    upload_bankinter_movements()