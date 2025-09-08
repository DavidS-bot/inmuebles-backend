#!/usr/bin/env python3
"""
Usar CSV descargado esta mañana y subirlo al agente financiero
"""

import pandas as pd
import requests
from datetime import datetime
import sys
import os

# Agregar app al path
app_path = os.path.join(os.path.dirname(__file__), 'app')
sys.path.insert(0, app_path)

# Importar el uploader
from services.financial_agent_uploader import upload_bankinter_excel

def procesar_csv_de_hoy():
    """Procesar CSV de esta mañana y subirlo"""
    
    csv_file = "bankinter_agente_financiero_20250828_105840.csv"
    
    print("="*60)
    print("[CSV] PROCESANDO DATOS DE BANKINTER DE HOY")
    print("="*60)
    print(f"Archivo: {csv_file}")
    
    if not os.path.exists(csv_file):
        print(f"[ERROR] No se encuentra el archivo {csv_file}")
        return False
    
    # Leer CSV
    try:
        print("[CSV] Leyendo datos...")
        df = pd.read_csv(csv_file, sep='\\t', encoding='utf-8-sig')  # Tab separated, UTF-8 with BOM
        print(f"[CSV] Filas leídas: {len(df)}")
        print(f"[CSV] Columnas: {list(df.columns)}")
        
        # Mostrar muestra
        print("[CSV] Muestra de datos:")
        for i in range(min(5, len(df))):
            row = df.iloc[i]
            print(f"  {i+1}. {row['Fecha']} | {row['Concepto'][:30]} | {row['Importe']}")
            
    except Exception as e:
        print(f"[ERROR] Error leyendo CSV: {e}")
        try:
            # Intentar con separador diferente
            df = pd.read_csv(csv_file, sep=',', encoding='utf-8-sig')
            print(f"[CSV] Reintento exitoso - Filas: {len(df)}")
        except:
            print("[ERROR] No se pudo leer el CSV")
            return False
    
    # Convertir a formato Excel temporal
    excel_file = csv_file.replace('.csv', '.xlsx')
    
    try:
        print("[EXCEL] Convirtiendo a Excel...")
        
        # Procesar datos para formato correcto
        df_processed = df.copy()
        
        # Limpiar importes - convertir de "27,00" a 27.0
        df_processed['Importe'] = df_processed['Importe'].astype(str)
        df_processed['Importe'] = df_processed['Importe'].str.replace(',', '.').astype(float)
        
        # Convertir fechas
        df_processed['Fecha'] = pd.to_datetime(df_processed['Fecha'], format='%d/%m/%Y')
        
        # Ordenar por fecha
        df_processed = df_processed.sort_values('Fecha')
        
        # Guardar como Excel
        df_processed.to_excel(excel_file, index=False)
        print(f"[EXCEL] Archivo Excel creado: {excel_file}")
        
    except Exception as e:
        print(f"[ERROR] Error creando Excel: {e}")
        return False
    
    # Subir usando el uploader automático
    try:
        print("[UPLOAD] Subiendo al Agente Financiero...")
        
        # Credenciales del agente
        agent_user = "davsanchez21277@gmail.com"
        agent_pass = "123456"
        
        # Usar el uploader del sistema
        result = upload_bankinter_excel(
            excel_file=excel_file,
            agent_username=agent_user,
            agent_password=agent_pass
        )
        
        if result:
            print("[SUCCESS] Datos subidos exitosamente al Agente Financiero!")
            print(f"[STATS] Movimientos procesados: {len(df_processed)}")
            print("[WEB] Verificar en: https://inmuebles-david.vercel.app/financial-agent/movements")
            return True
        else:
            print("[ERROR] Fallo en la subida automática")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error en subida: {e}")
        
        # Fallback: subida manual
        print("[FALLBACK] Intentando subida manual...")
        return subida_manual(df_processed, agent_user, agent_pass)

def subida_manual(df, username, password):
    """Subida manual al backend"""
    
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    # Login
    print("[LOGIN] Conectando al backend...")
    try:
        login_data = {"username": username, "password": password}
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
        print("[LOGIN] Login exitoso")
        
    except Exception as e:
        print(f"[ERROR] Error en login: {e}")
        return False
    
    # Subir movimientos
    uploaded = 0
    errors = 0
    duplicates = 0
    
    for index, row in df.iterrows():
        try:
            # Convertir fecha
            fecha = row['Fecha']
            if hasattr(fecha, 'strftime'):
                fecha_iso = fecha.strftime('%Y-%m-%d')
            else:
                fecha_iso = str(fecha)[:10]
            
            # Preparar movimiento
            movement = {
                "date": fecha_iso,
                "concept": str(row['Concepto']),
                "amount": float(row['Importe']),
                "category": "Sin clasificar"
            }
            
            # Intentar subir
            response = requests.post(
                f"{backend_url}/financial-movements/",
                json=movement,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 201:
                uploaded += 1
                print(f"[OK] {uploaded:2d}. {fecha_iso} | {row['Concepto'][:30]} | {row['Importe']} EUR")
            elif "exists" in response.text.lower():
                duplicates += 1
                print(f"[DUP] {duplicates:2d}. Duplicado: {row['Concepto'][:30]}")
            else:
                errors += 1
                print(f"[ERR] {errors:2d}. Error {response.status_code}: {row['Concepto'][:30]}")
                
        except Exception as e:
            errors += 1
            print(f"[ERR] Error procesando fila {index}: {e}")
    
    # Resumen
    total = uploaded + duplicates + errors
    print("\\n" + "="*50)
    print("[RESUMEN] RESULTADO DE SUBIDA MANUAL")
    print("="*50)
    print(f"[SUCCESS] Subidos: {uploaded}")
    print(f"[DUP] Duplicados: {duplicates}")
    print(f"[ERROR] Errores: {errors}")
    print(f"[TOTAL] Procesados: {total}")
    
    if uploaded > 0:
        print("\\n[SUCCESS] Algunos movimientos se subieron correctamente")
        return True
    else:
        print("\\n[INFO] No se subieron movimientos nuevos")
        return False

def main():
    """Función principal"""
    try:
        success = procesar_csv_de_hoy()
        
        if success:
            print("\\n[COMPLETE] Proceso completado exitosamente!")
        else:
            print("\\n[COMPLETE] Proceso terminado con errores")
            
    except Exception as e:
        print(f"\\n[CRITICAL] Error crítico: {e}")

if __name__ == "__main__":
    main()