#!/usr/bin/env python3
"""
Bankinter Simple - Usando datos que ya funcionaron esta mañana
Proceso simple: usar el CSV que ya tienes + subir al agente financiero
"""

import pandas as pd
import asyncio
import requests
from datetime import datetime
import os
import sys

# Agregar app al path para importar el uploader
app_path = os.path.join(os.path.dirname(__file__), 'app')
sys.path.insert(0, app_path)

from services.financial_agent_uploader import FinancialAgentUploader

async def subir_bankinter_existente():
    """Usar los datos de Bankinter que ya funcionaron esta mañana"""
    
    print("="*60)
    print("🏦 BANKINTER - USANDO DATOS EXISTENTES QUE FUNCIONARON")
    print("="*60)
    
    # Usar el archivo que ya funcionó
    csv_file = "bankinter_agente_financiero_20250828_105840.csv"
    
    if not os.path.exists(csv_file):
        print(f"❌ No se encuentra el archivo: {csv_file}")
        print("📋 Archivos disponibles:")
        
        # Buscar archivos similares
        for file in os.listdir('.'):
            if 'bankinter' in file.lower() and file.endswith('.csv'):
                print(f"  - {file}")
        
        return False
    
    print(f"✅ Usando archivo: {csv_file}")
    
    # Leer y procesar CSV
    try:
        print("📊 Procesando datos...")
        df = pd.read_csv(csv_file, sep='\\t', encoding='utf-8-sig')
        
        print(f"📈 Movimientos encontrados: {len(df)}")
        print(f"📅 Rango de fechas: {df['Fecha'].min()} - {df['Fecha'].max()}")
        
        # Mostrar muestra
        print("\\n📋 MUESTRA DE DATOS:")
        for i in range(min(5, len(df))):
            row = df.iloc[i]
            print(f"  {i+1}. {row['Fecha']} | {row['Concepto'][:40]} | {row['Importe']}€")
        
        # Convertir a Excel para el uploader
        excel_file = csv_file.replace('.csv', '.xlsx')
        
        # Procesar datos correctamente
        df_clean = df.copy()
        df_clean['Importe'] = df_clean['Importe'].astype(str).str.replace(',', '.').astype(float)
        df_clean['Fecha'] = pd.to_datetime(df_clean['Fecha'], format='%d/%m/%Y')
        df_clean = df_clean.sort_values('Fecha', ascending=False)
        df_clean['Fecha'] = df_clean['Fecha'].dt.strftime('%d/%m/%Y')
        
        # Guardar Excel
        df_clean.to_excel(excel_file, index=False)
        print(f"💾 Excel creado: {excel_file}")
        
    except Exception as e:
        print(f"❌ Error procesando CSV: {e}")
        return False
    
    # Subir usando el uploader avanzado
    print("\\n🚀 SUBIENDO AL AGENTE FINANCIERO...")
    
    try:
        # Usar el uploader del sistema
        async with FinancialAgentUploader(
            base_url="https://inmuebles-backend-api.onrender.com",
            username="davsanchez21277@gmail.com",
            password="123456"
        ) as uploader:
            
            result = await uploader.upload_excel_file(excel_file)
            
            if result.get('success'):
                uploaded = result.get('uploaded', 0)
                duplicates = result.get('duplicates', 0)
                errors = result.get('errors', 0)
                
                print("\\n" + "="*50)
                print("🎉 SUBIDA COMPLETADA")
                print("="*50)
                print(f"✅ Movimientos subidos: {uploaded}")
                print(f"🔄 Duplicados omitidos: {duplicates}")
                print(f"❌ Errores: {errors}")
                
                if uploaded > 0:
                    print(f"\\n🌐 ¡Revisa los datos en:")
                    print("    https://inmuebles-david.vercel.app/financial-agent/movements")
                    return True
                else:
                    print("\\nℹ️  No se agregaron movimientos nuevos (posiblemente ya existen)")
                    return True
            else:
                print(f"❌ Error en subida: {result.get('error', 'Unknown error')}")
                return False
                
    except Exception as e:
        print(f"❌ Error con uploader avanzado: {e}")
        
        # Fallback: subida manual tradicional
        print("\\n🔄 Intentando subida manual...")
        return await subida_manual_fallback(df_clean)

async def subida_manual_fallback(df):
    """Fallback con subida manual tradicional"""
    
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    # Login
    print("🔐 Login manual...")
    try:
        login_data = {"username": "davsanchez21277@gmail.com", "password": "123456"}
        response = requests.post(
            f"{backend_url}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Login fallido: {response.status_code}")
            return False
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        print("✅ Login exitoso")
        
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return False
    
    # Subir movimientos
    uploaded = 0
    duplicates = 0
    errors = 0
    
    print("📤 Subiendo movimientos...")
    
    for index, row in df.iterrows():
        try:
            # Convertir fecha
            if isinstance(row['Fecha'], str):
                fecha = pd.to_datetime(row['Fecha'], format='%d/%m/%Y')
            else:
                fecha = row['Fecha']
            
            fecha_iso = fecha.strftime('%Y-%m-%d')
            
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
                if uploaded % 5 == 0:  # Mostrar progreso cada 5
                    print(f"   📈 Subidos: {uploaded}")
                    
            elif "exists" in response.text.lower() or response.status_code == 409:
                duplicates += 1
                
            else:
                errors += 1
                if errors <= 3:  # Solo mostrar primeros 3 errores
                    print(f"   ❌ Error {response.status_code}: {row['Concepto'][:30]}")
                    
        except Exception as e:
            errors += 1
            
    # Resumen final
    total = uploaded + duplicates + errors
    print("\\n" + "="*50)
    print("📊 RESULTADO FINAL")
    print("="*50)
    print(f"✅ Nuevos movimientos: {uploaded}")
    print(f"🔄 Duplicados: {duplicates}")
    print(f"❌ Errores: {errors}")
    print(f"📋 Total procesados: {total}")
    
    if uploaded > 0:
        print(f"\\n🎉 ¡Éxito! {uploaded} movimientos agregados.")
        print("🌐 Verifica en: https://inmuebles-david.vercel.app/financial-agent/movements")
        return True
    else:
        print("\\nℹ️  No se agregaron movimientos nuevos")
        return True

def main():
    """Función principal"""
    print("🚀 EJECUTANDO PROCESO BANKINTER SIMPLE...")
    
    try:
        success = asyncio.run(subir_bankinter_existente())
        
        if success:
            print("\\n🎯 PROCESO COMPLETADO EXITOSAMENTE")
        else:
            print("\\n⚠️  PROCESO TERMINADO CON PROBLEMAS")
            
    except Exception as e:
        print(f"\\n💥 ERROR CRÍTICO: {e}")

if __name__ == "__main__":
    main()