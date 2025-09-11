#!/usr/bin/env python3
"""
Test directo del scraping de Bankinter SIN servidor
"""
import sys
import os

def run_embedded_scraper():
    """Ejecutar el scraper embebido tal como está en el endpoint"""
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager
        import time
        from datetime import datetime
        
        print("INICIANDO SCRAPER REAL DE BANKINTER...")
        print("=" * 60)
        
        options = Options()
        # NO headless para ver que funciona
        # options.add_argument("--headless")
        options.add_argument("--no-sandbox") 
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        print("Configurando Chrome WebDriver...")
        try:
            driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        except:
            driver = webdriver.Chrome(options=options)
        
        print("Navegando a Bankinter.com...")
        driver.get("https://www.bankinter.com")
        time.sleep(3)
        
        # Manejar cookies
        print("Manejando cookies...")
        try:
            cookie_btn = WebDriverWait(driver, 8).wait(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Aceptar') or contains(text(), 'Accept')]"))
            )
            cookie_btn.click()
            time.sleep(2)
        except:
            print("   - No se encontró popup de cookies")
        
        # Buscar ACCESO CLIENTES
        print("Buscando ACCESO CLIENTES...")
        access_selectors = [
            "//a[contains(text(), 'ACCESO CLIENTES')]",
            "//a[contains(text(), 'Acceso clientes')]", 
            "//a[@href*='login']"
        ]
        
        access_link = None
        for selector in access_selectors:
            try:
                access_link = WebDriverWait(driver, 5).wait(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                print(f"   Encontrado con selector: {selector}")
                break
            except:
                continue
        
        if not access_link:
            raise Exception("NO SE ENCONTRO ACCESO CLIENTES")
            
        access_link.click()
        print("Haciendo clic en ACCESO CLIENTES...")
        time.sleep(5)
        
        # Login
        print("Realizando login...")
        user_selectors = ["#userName", "#username", "input[name='username']", "input[type='text']"]
        pass_selectors = ["#password", "input[name='password']", "input[type='password']"]
        
        # Username
        user_field = None
        for selector in user_selectors:
            try:
                user_field = WebDriverWait(driver, 5).wait(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                print(f"   ✅ Campo usuario encontrado: {selector}")
                break
            except:
                continue
        
        if not user_field:
            raise Exception("❌ NO SE ENCONTRÓ CAMPO DE USUARIO")
            
        user_field.clear()
        user_field.send_keys("75867185")
        print("   ✅ Usuario ingresado")
        
        # Password
        pass_field = None
        for selector in pass_selectors:
            try:
                pass_field = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"   ✅ Campo contraseña encontrado: {selector}")
                break
            except:
                continue
                
        if not pass_field:
            raise Exception("❌ NO SE ENCONTRÓ CAMPO DE CONTRASEÑA")
            
        pass_field.clear()
        pass_field.send_keys("Motoreta123$")
        print("   ✅ Contraseña ingresada")
        
        # Botón login
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
                print(f"   ✅ Botón login encontrado: {selector}")
                break
            except:
                continue
                
        if not login_button:
            raise Exception("❌ NO SE ENCONTRÓ BOTÓN DE LOGIN")
            
        login_button.click()
        print("🚀 Login enviado, esperando respuesta...")
        time.sleep(10)
        
        # Buscar movimientos
        print("💰 Buscando tabla de movimientos...")
        movements = []
        
        movement_selectors = [
            "//table//tr",
            "//tbody//tr", 
            ".movement-row",
            ".transaction-row"
        ]
        
        movement_rows = []
        for selector in movement_selectors:
            try:
                if selector.startswith("//"):
                    movement_rows = driver.find_elements(By.XPATH, selector)
                else:
                    movement_rows = driver.find_elements(By.CSS_SELECTOR, selector)
                if len(movement_rows) > 0:
                    print(f"   ✅ Encontradas {len(movement_rows)} filas con: {selector}")
                    break
            except:
                continue
        
        print(f"📊 Procesando {len(movement_rows)} filas de movimientos...")
        
        # Extraer datos
        for i, row in enumerate(movement_rows[:20]):
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
                        print(f"   📋 {date} | {concept} | {amount}")
            except Exception as e:
                print(f"   ⚠️  Error procesando fila {i}: {e}")
                continue
        
        driver.quit()
        
        result = {
            "success": True,
            "movements": movements,
            "count": len(movements),
            "method": "embedded_scraping_test",
            "message": f"✅ SCRAPING EXITOSO: {len(movements)} movimientos extraídos",
            "timestamp": datetime.now().isoformat()
        }
        
        print("=" * 60)
        print(f"🎉 RESULTADO FINAL: {result['message']}")
        print(f"📊 Total movimientos: {len(movements)}")
        print("=" * 60)
        
        return result
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "method": "embedded_scraping_failed",
            "timestamp": datetime.now().isoformat()
        }
        print(f"❌ ERROR: {error_result}")
        return error_result

if __name__ == "__main__":
    print("🧪 PROBANDO SCRAPER EMBEBIDO DE BANKINTER...")
    result = run_embedded_scraper()
    
    if result["success"]:
        print(f"\n✅ SUCCESS: Extraídos {result['count']} movimientos")
        for mov in result["movements"][:5]:  # Mostrar solo los primeros 5
            print(f"   - {mov['date']} | {mov['concept']} | {mov['amount']}")
    else:
        print(f"\n❌ FAILED: {result['error']}")