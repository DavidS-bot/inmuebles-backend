#!/usr/bin/env python3
"""
Subir datos existentes de Bankinter al backend usando CSVs que ya tienes
"""

import pandas as pd
import requests
from datetime import datetime
import os
import glob

def find_latest_bankinter_csv():
    """Find the most recent Bankinter CSV file"""
    
    # Buscar archivos CSV de Bankinter
    patterns = [
        "bankinter_movimientos_*.csv",
        "bankinter_export_*.csv"
    ]
    
    all_files = []
    for pattern in patterns:
        files = glob.glob(pattern)
        all_files.extend(files)
    
    if not all_files:
        print("[ERROR] No se encontraron archivos CSV de Bankinter")
        return None
    
    # Ordenar por fecha de modificación
    all_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    print(f"[CSV] Archivos encontrados:")
    for i, file in enumerate(all_files[:5]):
        size = os.path.getsize(file)
        mod_time = datetime.fromtimestamp(os.path.getmtime(file))
        print(f"  {i+1}. {file} ({size} bytes, {mod_time.strftime('%Y-%m-%d %H:%M')})")
    
    # Usar el archivo con más datos (el segundo más reciente)
    return all_files[1] if len(all_files) > 1 else all_files[0]

def upload_csv_to_backend(csv_file):
    """Upload CSV data to backend"""
    
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    # Login
    print("[LOGIN] Conectando al backend...")
    login_data = {"username": "davsanchez21277@gmail.com", "password": "123456"}
    
    try:
        response = requests.post(
            f"{backend_url}/auth/login", 
            data=login_data, 
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"[ERROR] Login fallido: {response.status_code}")
            return False
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        print("[SUCCESS] Login exitoso")
        
    except Exception as e:
        print(f"[ERROR] Error en login: {e}")
        return False
    
    # Leer CSV
    print(f"[CSV] Leyendo {csv_file}...")
    
    try:
        df = pd.read_csv(csv_file, encoding='utf-8')
        print(f"[CSV] Leidas {len(df)} filas")
        print(f"[CSV] Columnas: {list(df.columns)}")
        
        # Mostrar muestra
        print("[CSV] Muestra de datos:")
        for i in range(min(3, len(df))):
            print(f"  Fila {i+1}: {dict(df.iloc[i])}")
        
    except Exception as e:
        print(f"[ERROR] Error leyendo CSV: {e}")
        return False
    
    # Filtrar movimientos reales (excluir saldos)
    if 'Categoria' in df.columns:
        df_movements = df[~df['Categoria'].isin(['Saldo'])].copy()
        print(f"[FILTER] Movimientos financieros: {len(df_movements)}")
    else:
        df_movements = df.copy()
        print(f"[INFO] Procesando todas las filas como movimientos")
    
    uploaded = 0
    duplicates = 0
    errors = 0
    
    # Procesar cada movimiento
    for index, row in df_movements.iterrows():
        try:
            # Determinar estructura según columnas disponibles
            if 'Fecha' in row and 'Concepto' in row and 'Importe' in row:
                # Formato estándar
                fecha_str = str(row['Fecha'])
                concepto = str(row['Concepto'])
                importe = float(row['Importe'])
                
                # Convertir fecha
                try:
                    if '/' in fecha_str:
                        fecha_dt = datetime.strptime(fecha_str, '%d/%m/%Y')
                    else:
                        fecha_dt = datetime.strptime(fecha_str, '%Y-%m-%d')
                    
                    # Corregir fechas futuras
                    if fecha_dt.year > 2024:
                        fecha_dt = fecha_dt.replace(year=2024)
                        
                    fecha_iso = fecha_dt.strftime('%Y-%m-%d')
                    
                except:
                    print(f"[SKIP] Fecha inválida en fila {index}: {fecha_str}")
                    continue
                
                # Preparar movimiento
                movement_data = {
                    "date": fecha_iso,
                    "concept": concepto,
                    "amount": importe,
                    "category": "Sin clasificar"
                }
                
                # Intentar subir SIN property_id primero
                try:
                    response = requests.post(
                        f"{backend_url}/financial-movements/", 
                        json=movement_data, 
                        headers=headers,
                        timeout=10
                    )
                    
                    if response.status_code == 201:
                        uploaded += 1
                        print(f"[OK] {uploaded:2d}. {fecha_iso} | {concepto[:40]} | {importe} EUR")
                        
                    elif response.status_code == 422 and "property_id" in response.text:
                        # Retry with property_id
                        movement_data["property_id"] = 1
                        response = requests.post(
                            f"{backend_url}/financial-movements/", 
                            json=movement_data, 
                            headers=headers,
                            timeout=10
                        )
                        
                        if response.status_code == 201:
                            uploaded += 1
                            print(f"[OK] {uploaded:2d}. {fecha_iso} | {concepto[:40]} | {importe} EUR (con property_id)")
                        else:
                            errors += 1
                            print(f"[ERR] {errors:2d}. Error {response.status_code}: {concepto[:30]} - {response.text[:50]}")
                            
                    elif "already exists" in response.text.lower() or "duplicate" in response.text.lower():
                        duplicates += 1
                        print(f"[DUP] {duplicates:2d}. Duplicado: {fecha_iso} | {concepto[:40]}")
                        
                    else:
                        errors += 1
                        print(f"[ERR] {errors:2d}. Error {response.status_code}: {concepto[:30]} - {response.text[:50]}")
                        
                except requests.exceptions.RequestException as e:
                    errors += 1
                    print(f"[ERR] {errors:2d}. Error de red: {concepto[:30]} - {e}")
                    
            else:
                print(f"[SKIP] Fila {index} no tiene estructura esperada: {list(row.index)}")
                
        except Exception as e:
            errors += 1
            print(f"[ERR] {errors:2d}. Error procesando fila {index}: {e}")
    
    # Resumen
    total = uploaded + duplicates + errors
    print("\\n" + "="*60)
    print("[RESUMEN] RESULTADO DE LA IMPORTACION")
    print("="*60)
    print(f"[SUCCESS] Nuevos movimientos subidos: {uploaded}")
    print(f"[DUP] Duplicados omitidos: {duplicates}")
    print(f"[ERROR] Errores encontrados: {errors}")
    print(f"[TOTAL] Movimientos procesados: {total}")
    
    if uploaded > 0:
        print(f"\\n[SUCCESS] ¡Importación exitosa! {uploaded} movimientos agregados al sistema.")
        print("\\n[NEXT] Próximos pasos:")
        print("1. Ve a: https://inmuebles-david.vercel.app/financial-agent/movements")
        print("2. Verifica que aparezcan los nuevos movimientos")
        print("3. Las reglas de clasificación se aplicarán automáticamente")
        return True
    else:
        print("\\n[INFO] No se agregaron movimientos nuevos")
        return False

def main():
    """Main function"""
    print("IMPORTACION DE DATOS EXISTENTES DE BANKINTER")
    print("="*50)
    
    # Encontrar CSV más reciente
    csv_file = find_latest_bankinter_csv()
    if not csv_file:
        return
    
    print(f"[SELECTED] Usando archivo: {csv_file}")
    
    # Subir al backend
    success = upload_csv_to_backend(csv_file)
    
    if success:
        print("\\n[COMPLETE] ¡Proceso completado exitosamente!")
    else:
        print("\\n[COMPLETE] Proceso terminado - revisa los errores arriba")

if __name__ == "__main__":
    main()