#!/usr/bin/env python3
"""
Bankinter Real Scraper - Versión robusta con manejo automático de ChromeDriver
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import requests
import pandas as pd
from datetime import datetime
import csv
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_robust_driver():
    """Create a robust Chrome driver with automatic driver management"""
    
    # Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Use WebDriver Manager to handle ChromeDriver automatically
    service = Service(ChromeDriverManager().install())
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def scrape_bankinter_real():
    """Scrape real Bankinter data from web"""
    
    # Credenciales
    username = "75867185"
    password = "Motoreta123$"
    
    logger.info("[BANKINTER] 🏦 Iniciando scraping REAL de Bankinter...")
    
    driver = None
    try:
        # Create driver
        logger.info("[BANKINTER] 📱 Creando navegador Chrome...")
        driver = create_robust_driver()
        wait = WebDriverWait(driver, 30)
        
        # Go to Bankinter
        logger.info("[BANKINTER] 🌐 Navegando a bankinter.com...")
        driver.get("https://www.bankinter.com")
        time.sleep(5)
        
        # Handle GDPR/Cookies popup
        logger.info("[BANKINTER] 🍪 Manejando popup de cookies...")
        try:
            cookie_selectors = [
                "#onetrust-accept-btn-handler",
                ".ot-sdk-row .ot-sdk-columns button",
                "button[aria-label*='Acepto']",
                "button[contains(text(), 'Acepto')]",
                ".onetrust-close-btn-handler",
                ".optanon-alert-box-close"
            ]
            
            for selector in cookie_selectors:
                try:
                    if selector.startswith("//"):
                        cookie_btn = driver.find_element(By.XPATH, selector)
                    else:
                        cookie_btn = driver.find_element(By.CSS_SELECTOR, selector)
                    cookie_btn.click()
                    logger.info("[BANKINTER] ✅ Popup de cookies cerrado")
                    time.sleep(2)
                    break
                except:
                    continue
        except Exception as e:
            logger.info("[BANKINTER] ℹ️  No se encontró popup de cookies")
        
        # Find and click login button
        logger.info("[BANKINTER] 🔍 Buscando botón de login...")
        try:
            # Try multiple selectors for login button
            login_selectors = [
                "//a[contains(@href, 'login')]",
                "//a[contains(text(), 'Acceso')]",
                "//button[contains(text(), 'Acceso')]",
                "[data-testid='login']",
                ".login-button"
            ]
            
            login_button = None
            for selector in login_selectors:
                try:
                    if selector.startswith("//"):
                        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    else:
                        login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    break
                except:
                    continue
            
            if not login_button:
                raise Exception("No se encontró el botón de login")
            
            # Try regular click first, then JavaScript click if intercepted
            try:
                login_button.click()
            except:
                logger.info("[BANKINTER] 🔧 Click interceptado, usando JavaScript...")
                driver.execute_script("arguments[0].click();", login_button)
            time.sleep(5)
            
        except Exception as e:
            logger.error(f"[ERROR] Error finding login button: {e}")
            driver.save_screenshot("bankinter_login_error.png")
            raise
        
        # Enter credentials
        logger.info("[BANKINTER] 🔐 Introduciendo credenciales...")
        
        # Username
        user_selectors = [
            "input[name='documento']",
            "input[id*='usuario']",
            "input[placeholder*='documento']",
            "#documento",
            "[data-testid='username']"
        ]
        
        user_field = None
        for selector in user_selectors:
            try:
                user_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                break
            except:
                continue
        
        if not user_field:
            raise Exception("No se encontró el campo de usuario")
            
        user_field.clear()
        user_field.send_keys(username)
        time.sleep(1)
        
        # Password
        pass_selectors = [
            "input[name='clave']",
            "input[type='password']",
            "input[id*='password']",
            "#clave",
            "[data-testid='password']"
        ]
        
        pass_field = None
        for selector in pass_selectors:
            try:
                pass_field = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except:
                continue
        
        if not pass_field:
            raise Exception("No se encontró el campo de contraseña")
            
        pass_field.clear()
        pass_field.send_keys(password)
        time.sleep(1)
        
        # Submit login
        logger.info("[BANKINTER] 🚀 Haciendo login...")
        submit_selectors = [
            "input[type='submit']",
            "button[type='submit']",
            "input[value*='Entrar']",
            "button[contains(text(), 'Entrar')]",
            ".submit-button"
        ]
        
        login_submit = None
        for selector in submit_selectors:
            try:
                if selector.startswith("//"):
                    login_submit = driver.find_element(By.XPATH, selector)
                else:
                    login_submit = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except:
                continue
        
        if not login_submit:
            raise Exception("No se encontró el botón de envío")
            
        login_submit.click()
        
        logger.info("[BANKINTER] ⏳ Esperando login...")
        time.sleep(10)
        
        # Navigate to movements
        logger.info("[BANKINTER] 💰 Navegando a movimientos...")
        
        # Look for EUR account
        account_selectors = [
            "//*[contains(text(), 'Cc Euros')]",
            "//*[contains(text(), 'EUR')]",
            "//*[contains(text(), 'Cuenta')]",
            ".account-euro",
            "[data-currency='EUR']"
        ]
        
        eur_account = None
        for selector in account_selectors:
            try:
                if selector.startswith("//"):
                    eur_account = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                else:
                    eur_account = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                break
            except:
                continue
        
        if not eur_account:
            logger.warning("[WARNING] No se encontró cuenta EUR, buscando movimientos directamente...")
        else:
            eur_account.click()
            time.sleep(5)
        
        # Extract movements
        logger.info("[BANKINTER] 📊 Extrayendo movimientos...")
        movements = []
        
        # Try different selectors for movement rows
        movement_selectors = [
            "//tr[contains(@class, 'movement')]",
            "//tr[contains(@class, 'row')]",
            "//div[contains(@class, 'movement')]",
            ".transaction-row",
            ".movement-item",
            "[data-testid='transaction']"
        ]
        
        movement_rows = []
        for selector in movement_selectors:
            try:
                if selector.startswith("//"):
                    movement_rows = driver.find_elements(By.XPATH, selector)
                else:
                    movement_rows = driver.find_elements(By.CSS_SELECTOR, selector)
                if movement_rows:
                    break
            except:
                continue
        
        if not movement_rows:
            logger.error("[ERROR] No se encontraron movimientos")
            driver.save_screenshot("bankinter_no_movements.png")
            # Get page source for debugging
            with open("bankinter_page_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            return None
        
        logger.info(f"[BANKINTER] ✅ Encontradas {len(movement_rows)} filas de movimientos")
        
        for i, row in enumerate(movement_rows[:30]):  # Process last 30 movements
            try:
                text = row.text.strip()
                if text and len(text) > 10:
                    logger.info(f"[MOVEMENT {i+1}] {text[:100]}...")
                    movements.append({
                        'raw_text': text,
                        'row_number': i + 1,
                        'extracted_at': datetime.now().isoformat()
                    })
                        
            except Exception as e:
                logger.error(f"[ERROR] Error processing movement {i}: {e}")
        
        # Create output file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"bankinter_real_extraction_{timestamp}.csv"
        
        # Save raw extractions
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Fecha', 'Concepto', 'Importe'])
            
            for movement in movements:
                # Try to parse movement text
                try:
                    # Basic parsing attempt - this would need refinement based on actual HTML structure
                    text = movement['raw_text']
                    # This is a placeholder - actual parsing would depend on Bankinter's HTML structure
                    parts = text.split()
                    if len(parts) >= 3:
                        fecha = parts[0] if '/' in parts[0] else datetime.now().strftime('%d/%m/%Y')
                        concepto = ' '.join(parts[1:-1]) if len(parts) > 2 else 'Concepto no identificado'
                        importe = parts[-1] if parts[-1].replace(',', '').replace('-', '').replace('+', '').replace('€', '').replace('.', '').isdigit() else '0,00'
                        
                        writer.writerow([fecha, concepto, importe])
                except Exception as e:
                    logger.error(f"[ERROR] Error parsing movement: {e}")
        
        logger.info(f"[SUCCESS] ✅ Datos guardados en: {output_file}")
        logger.info(f"[EXTRACTED] 📊 {len(movements)} movimientos procesados")
        
        return output_file
        
    except Exception as e:
        logger.error(f"[ERROR] ❌ Error durante scraping: {e}")
        if driver:
            driver.save_screenshot(f"bankinter_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        return None
        
    finally:
        if driver:
            driver.quit()

def process_and_upload_to_api(csv_file):
    """Process extracted data and upload to API"""
    
    if not csv_file or not os.path.exists(csv_file):
        logger.error("[ERROR] ❌ No se encontró archivo de datos")
        return False
    
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    # Login to API
    logger.info("[API] 🔐 Haciendo login al backend...")
    try:
        login_data = {"username": "davsanchez21277@gmail.com", "password": "123456"}
        response = requests.post(
            f"{backend_url}/auth/login", 
            data=login_data, 
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30
        )
        
        if response.status_code != 200:
            logger.error(f"[ERROR] ❌ Login fallido: {response.status_code}")
            return False
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        logger.info("[API] ✅ Login exitoso")
        
    except Exception as e:
        logger.error(f"[ERROR] ❌ Error en login: {e}")
        return False
    
    # Read and process CSV
    movements_data = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                movements_data.append(row)
    except Exception as e:
        logger.error(f"[ERROR] ❌ Error leyendo CSV: {e}")
        return False
    
    logger.info(f"[API] 📊 Subiendo {len(movements_data)} movimientos...")
    
    uploaded = 0
    duplicates = 0
    errors = 0
    
    for movement in movements_data:
        try:
            # Parse movement data
            fecha_str = movement['Fecha']
            if '/' in fecha_str:
                fecha_parts = fecha_str.split('/')
                fecha = f"{fecha_parts[2]}-{fecha_parts[1]}-{fecha_parts[0]}"  # Convert to YYYY-MM-DD
            else:
                fecha = datetime.now().strftime('%Y-%m-%d')
            
            importe_str = movement['Importe'].replace(',', '.').replace('€', '').strip()
            try:
                importe = float(importe_str)
            except:
                importe = 0.0
            
            concepto = movement['Concepto']
            
            # Create movement object
            movement_obj = {
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
                if uploaded % 5 == 0:
                    logger.info(f"[API] ✅ Subidos: {uploaded}")
            elif "exists" in response.text.lower() or response.status_code == 409:
                duplicates += 1
            else:
                errors += 1
                if errors <= 3:
                    logger.error(f"[API] ❌ Error {response.status_code}: {concepto[:30]}")
                    
        except Exception as e:
            errors += 1
            logger.error(f"[ERROR] ❌ Error procesando movimiento: {e}")
    
    # Final summary
    logger.info("[RESULT] 🎉 RESULTADO FINAL:")
    logger.info(f"[RESULT] ✅ Nuevos movimientos: {uploaded}")
    logger.info(f"[RESULT] 🔄 Duplicados: {duplicates}")
    logger.info(f"[RESULT] ❌ Errores: {errors}")
    
    return uploaded > 0

def main():
    """Main function"""
    logger.info("🚀 SCRAPER REAL DE BANKINTER - INICIANDO")
    logger.info("="*60)
    
    # Step 1: Scrape real data from Bankinter
    csv_file = scrape_bankinter_real()
    
    if not csv_file:
        logger.error("[ERROR] ❌ No se pudieron obtener los datos de Bankinter")
        return False
    
    # Step 2: Process and upload to API
    success = process_and_upload_to_api(csv_file)
    
    if success:
        logger.info("[SUCCESS] 🎉 PROCESO COMPLETADO EXITOSAMENTE!")
        logger.info("[SUCCESS] 🌐 Ve a: https://inmuebles-web.vercel.app/financial-agent/movements")
        return True
    else:
        logger.error("[ERROR] ❌ Hubo problemas durante la subida")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)