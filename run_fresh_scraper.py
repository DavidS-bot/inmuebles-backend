#!/usr/bin/env python3
"""
Run FRESH Bankinter scraper (always scrapes, never uses cached files)
"""

import os
import glob
import requests
from datetime import datetime
import subprocess
import sys

def run_fresh_scraper_and_upload():
    """ALWAYS run fresh scraper, never use cached files"""
    
    print("EJECUTANDO SCRAPER FRESCO DE BANKINTER...")
    print("AVISO: Este proceso SIEMPRE descarga datos nuevos de la web")
    
    try:
        print("Iniciando scraper automático de Bankinter...")
        print("Este proceso:")
        print("   1. Abrirá Chrome")
        print("   2. Se conectará a Bankinter")
        print("   3. Descargará datos actuales") 
        print("   4. Los subirá automáticamente")
        
        # Execute bankinter_simple_working.py which was working this morning
        result = subprocess.run(
            [sys.executable, 'bankinter_simple_working.py'], 
            capture_output=True, 
            text=True, 
            timeout=300  # 5 minute timeout
        )
        
        print(f"Scraper return code: {result.returncode}")
        print(f"Scraper stdout: {result.stdout[:500]}...")
        print(f"Scraper stderr: {result.stderr[:500]}...")
        
        if result.returncode == 0:
            print("Scraper ejecutado exitosamente!")
            
            # Look for Excel files created by the working script
            pattern = "bankinter_agente_financiero_*.xlsx"
            files = glob.glob(pattern)
            
            if files:
                # Get the most recent file
                latest_file = max(files, key=os.path.getmtime)
                print(f"Archivo procesado: {latest_file}")
                print("Subiendo archivo procesado...")
                return upload_file(latest_file)
            
            # If no agente financiero file, try API files
            pattern2 = "bankinter_api_*.xlsx" 
            files2 = glob.glob(pattern2)
            
            if files2:
                latest_file = max(files2, key=os.path.getmtime)
                mod_time = datetime.fromtimestamp(os.path.getmtime(latest_file))
                time_diff = (datetime.now() - mod_time).total_seconds()
                
                if time_diff < 300:  # Less than 5 minutes old
                    print(f"Archivo recién generado: {latest_file}")
                    return upload_file(latest_file)
            
            print("AVISO: No se encontraron archivos para subir")
            return False
            
        else:
            print(f"ERROR: Scraper falló:")
            print(f"   stdout: {result.stdout}")
            print(f"   stderr: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("ERROR: El scraper tardó más de 5 minutos")
        return False
    except Exception as e:
        print(f"ERROR ejecutando scraper: {e}")
        return False

def upload_file(filepath):
    """Upload file to production backend"""
    
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    print(f"Subiendo {filepath} a producción...")
    
    try:
        # Login
        login_data = {'username': 'davsanchez21277@gmail.com', 'password': '123456'}
        response = requests.post(
            f'{backend_url}/auth/login',
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"ERROR: Login falló: {response.status_code}")
            return False
        
        token = response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Upload file
        with open(filepath, 'rb') as file:
            files = {'file': (filepath, file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            response = requests.post(
                f'{backend_url}/financial-movements/upload-excel-global',
                files=files,
                headers=headers,
                timeout=60
            )
        
        if response.status_code == 200:
            result = response.json()
            
            print("Subida exitosa!")
            print(f"Movimientos creados: {result.get('created_movements', 0)}")
            print(f"Total filas: {result.get('total_rows', 0)}")
            print(f"Duplicados omitidos: {result.get('duplicates_skipped', 0)}")
            return True
        else:
            print(f"ERROR: Subida falló: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"ERROR subiendo: {e}")
        return False

if __name__ == "__main__":
    success = run_fresh_scraper_and_upload()
    if success:
        print("ÉXITO! Scraper fresco ejecutado y subido a producción")
    else:
        print("FALLÓ: No se pudo completar el scraping fresco")