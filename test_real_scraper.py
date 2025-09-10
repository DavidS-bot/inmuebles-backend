#!/usr/bin/env python3
"""
Test del scraper REAL de Bankinter
"""
import os
import sys
from datetime import datetime
import json

def scrape_bankinter_real():
    """Scraping REAL de Bankinter con Selenium"""
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager
        import time
        
        print("Iniciando navegador para Bankinter...")
        
        options = Options()
        # NO usar headless para poder ver que funciona
        # options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        # Usar WebDriverManager para gestión automática
        try:
            driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        except:
            # Fallback si WebDriverManager falla
            driver = webdriver.Chrome(options=options)
        
        print("Navegando a Bankinter...")
        driver.get("https://www.bankinter.com")
        time.sleep(3)
        
        # Manejar popup de cookies
        try:
            print("Manejando cookies...")
            accept_button = WebDriverWait(driver, 10).wait(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Aceptar')] | //button[contains(text(), 'Accept')] | //button[@id='onetrust-accept-btn-handler']"))
            )
            accept_button.click()
            time.sleep(2)
        except:
            print("No se encontro popup de cookies")
        
        # Buscar y hacer clic en ACCESO CLIENTES
        print("Buscando acceso clientes...")
        access_selectors = [
            "//a[contains(text(), 'ACCESO CLIENTES')]",
            "//a[contains(text(), 'Acceso clientes')]", 
            "//a[@href*='login']",
            "//a[contains(@class, 'login')]"
        ]
        
        access_link = None
        for selector in access_selectors:
            try:
                access_link = WebDriverWait(driver, 5).wait(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                break
            except:
                continue
        
        if not access_link:
            raise Exception("No se encontro el enlace de acceso clientes")
            
        access_link.click()
        print("Acceso clientes encontrado y clickeado")
        time.sleep(5)
        
        # Login
        print("Realizando login...")
        user_selectors = ["#userName", "#username", "input[name='username']", "input[type='text']"]
        pass_selectors = ["#password", "input[name='password']", "input[type='password']"]
        
        user_field = None
        for selector in user_selectors:
            try:
                user_field = WebDriverWait(driver, 5).wait(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                break
            except:
                continue
        
        if not user_field:
            raise Exception("No se encontro el campo de usuario")
            
        user_field.clear()
        user_field.send_keys("75867185")
        
        pass_field = None
        for selector in pass_selectors:
            try:
                pass_field = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except:
                continue
                
        if not pass_field:
            raise Exception("No se encontro el campo de contraseña")
            
        pass_field.clear()
        pass_field.send_keys("Motoreta123$")
        
        # Buscar botón de login
        login_selectors = [
            "//input[@value='Entrar']",
            "//button[contains(text(), 'Entrar')]",
            "//input[@type='submit']",
            "//button[@type='submit']"
        ]
        
        login_button = None
        for selector in login_selectors:
            try:
                login_button = driver.find_element(By.XPATH, selector)
                break
            except:
                continue
                
        if not login_button:
            raise Exception("No se encontro el boton de login")
            
        login_button.click()
        print("Login enviado")
        time.sleep(10)  # Esperar más tiempo para el login
        
        # Buscar movimientos
        print("Buscando movimientos...")
        movements = []
        
        # Buscar tabla de movimientos
        movement_selectors = [
            "//table//tr",
            "//tbody//tr", 
            ".movement-row",
            ".transaction-row",
            "[data-testid*='movement']"
        ]
        
        movement_rows = []
        for selector in movement_selectors:
            try:
                if selector.startswith("//"):
                    movement_rows = driver.find_elements(By.XPATH, selector)
                else:
                    movement_rows = driver.find_elements(By.CSS_SELECTOR, selector)
                if len(movement_rows) > 0:
                    break
            except:
                continue
        
        print(f"Encontradas {len(movement_rows)} filas de movimientos")
        
        # Extraer datos de movimientos
        for i, row in enumerate(movement_rows[:20]):  # Limitar a 20 movimientos
            try:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 3:
                    date = cells[0].text.strip()
                    concept = cells[1].text.strip() 
                    amount = cells[2].text.strip()
                    
                    if date and concept and amount:
                        movements.append({
                            "date": date,
                            "concept": concept,
                            "amount": amount,
                            "index": i + 1
                        })
                        print(f"  {date} | {concept} | {amount}")
            except Exception as e:
                print(f"Error procesando fila {i}: {e}")
                continue
        
        driver.quit()
        
        result = {
            "success": True,
            "movements": movements,
            "count": len(movements),
            "method": "real_scraping",
            "message": f"SCRAPING REAL EXITOSO: {len(movements)} movimientos extraídos",
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"SUCCESS: {result}")
        return result
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "method": "real_scraping_failed",
            "timestamp": datetime.now().isoformat()
        }
        print(f"FAILED: {error_result}")
        return error_result

if __name__ == "__main__":
    print("PROBANDO SCRAPER REAL DE BANKINTER...")
    print("=" * 50)
    result = scrape_bankinter_real()
    print("=" * 50)
    print("RESULTADO FINAL:")
    print(json.dumps(result, indent=2))