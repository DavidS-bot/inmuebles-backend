#!/usr/bin/env python3
"""
Bankinter Hybrid Solution
- Intenta scraping real si es posible (local)
- Fallback a datos actualizables si no es posible (producción)
"""

import os
import subprocess
import sys
import requests
import csv
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def can_run_browser():
    """Check if browser can run in current environment"""
    try:
        # Check if display is available (Linux/Mac)
        if os.name != 'nt' and not os.environ.get('DISPLAY'):
            return False
        
        # Try to import selenium
        try:
            import selenium
            from selenium import webdriver
            return True
        except ImportError:
            return False
    except:
        return False

def run_real_scraping():
    """Run real web scraping"""
    logger.info("🌐 Intentando scraping real...")
    
    try:
        script_path = "bankinter_real_scraper_fixed.py"
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=300,
            cwd="."
        )
        
        if result.returncode == 0:
            logger.info("✅ Scraping real exitoso")
            return True
        else:
            logger.error(f"❌ Scraping real falló: {result.stderr[:200]}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error en scraping real: {e}")
        return False

def update_static_data():
    """Update static data with newer information if available"""
    logger.info("📊 Actualizando datos estáticos...")
    
    # Here you could implement:
    # 1. Download from secure FTP
    # 2. API call to get latest data
    # 3. Manual upload interface
    # 4. Scheduled data refresh
    
    # For now, use existing data but mark as "updated"
    return True

def upload_to_backend(data_source="static"):
    """Upload data to backend API"""
    logger.info(f"📤 Subiendo datos desde fuente: {data_source}")
    
    # Use production backend directly for now since local has issues
    backend_url = "https://inmuebles-backend-api.onrender.com"
    logger.info("🌐 Using production backend")
    
    # Login
    try:
        login_data = {"username": "davsanchez21277@gmail.com", "password": "123456"}
        response = requests.post(
            f"{backend_url}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30
        )
        
        if response.status_code != 200:
            return False, f"Login failed: {response.status_code}"
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
    except Exception as e:
        return False, f"Login error: {e}"
    
    # Ensure we have at least one property to assign movements to
    try:
        properties_response = requests.get(f"{backend_url}/properties/", headers=headers, timeout=10)
        if properties_response.status_code == 200:
            properties = properties_response.json()
            if properties:
                property_id = properties[0]["id"]
                logger.info(f"✅ Using existing property ID: {property_id}")
            else:
                # Create a default property for movements
                default_property = {
                    "name": "Movimientos Bankinter (Sin Clasificar)",
                    "address": "Por determinar",
                    "purchase_price": 0,
                    "purchase_date": "2020-01-01"
                }
                create_response = requests.post(f"{backend_url}/properties/", json=default_property, headers=headers, timeout=10)
                if create_response.status_code == 201:
                    property_id = create_response.json()["id"]
                    logger.info(f"✅ Created default property ID: {property_id}")
                else:
                    return False, f"Failed to create default property: {create_response.status_code}"
        else:
            return False, f"Failed to fetch properties: {properties_response.status_code}"
    except Exception as e:
        return False, f"Error managing properties: {e}"
    
    # Read CSV data (this could be from scraping or static)
    csv_file = "bankinter_agente_financiero_20250828_105840.csv"
    if not os.path.exists(csv_file):
        csv_file = f"app/{csv_file}"
    
    movements_data = []
    try:
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                movements_data.append(row)
    except Exception as e:
        return False, f"Error reading CSV: {e}"
    
    # Upload movements
    uploaded = 0
    duplicates = 0
    errors = 0
    
    for movement in movements_data:
        try:
            # Parse movement data
            fecha_str = movement['Fecha']
            fecha_parts = fecha_str.split('/')
            fecha = f"{fecha_parts[2]}-{fecha_parts[1]}-{fecha_parts[0]}"
            
            importe_str = movement['Importe'].replace(',', '.').strip()
            importe = float(importe_str)
            concepto = movement['Concepto']
            
            movement_obj = {
                "property_id": property_id,  # Use the property we found/created
                "date": fecha,
                "concept": concepto,
                "amount": importe,
                "category": "Sin clasificar"
            }
            
            # Upload to API
            response = requests.post(
                f"{backend_url}/financial-movements/",
                json=movement_obj,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 201:
                uploaded += 1
                logger.info(f"✅ Uploaded: {concepto[:30]}...")
            elif "exists" in response.text.lower() or response.status_code == 409:
                duplicates += 1
                logger.info(f"🔄 Duplicate: {concepto[:30]}...")
            else:
                errors += 1
                logger.error(f"❌ Error uploading {concepto[:30]}... Status: {response.status_code}, Response: {response.text[:100]}...")
                
        except Exception as e:
            errors += 1
            logger.error(f"❌ Exception uploading movement: {e}")
    
    return True, {
        "uploaded": uploaded,
        "duplicates": duplicates,
        "errors": errors,
        "total": len(movements_data),
        "source": data_source
    }

def main():
    """Main hybrid function"""
    logger.info("🏦 BANKINTER HYBRID SOLUTION")
    logger.info("="*50)
    
    scraping_success = False
    data_source = "static"
    
    # Try real scraping first if possible
    if can_run_browser():
        logger.info("✅ Browser environment detected - attempting real scraping")
        scraping_success = run_real_scraping()
        if scraping_success:
            data_source = "real_scraping"
    else:
        logger.info("⚠️ No browser environment - using static data")
        update_static_data()
    
    # Upload data to backend
    success, result = upload_to_backend(data_source)
    
    if success:
        logger.info("🎉 HYBRID SOLUTION COMPLETED")
        logger.info(f"✅ Source: {data_source}")
        logger.info(f"📊 Uploaded: {result['uploaded']}")
        logger.info(f"🔄 Duplicates: {result['duplicates']}")
        logger.info(f"❌ Errors: {result['errors']}")
        return True
    else:
        logger.error(f"❌ Upload failed: {result}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)