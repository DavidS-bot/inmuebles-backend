#!/usr/bin/env python3
"""
Test simple del scraping real de Bankinter
"""

def test_bankinter():
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager
        import time
        
        print("INICIANDO TEST DE SCRAPING REAL...")
        
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # NO headless para que veas la ventana
        
        from selenium.webdriver.chrome.service import Service
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        print("NAVEGANDO A BANKINTER.COM...")
        driver.get("https://www.bankinter.com")
        print(f"PAGINA CARGADA: {driver.title}")
        time.sleep(3)
        
        print("BUSCANDO ACCESO CLIENTES...")
        try:
            access_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'ACCESO CLIENTES') or contains(text(), 'Acceso clientes')]"))
            )
            print("ENLACE ENCONTRADO - Haciendo clic...")
            access_link.click()
            time.sleep(3)
            
            print(f"EXITO - URL actual: {driver.current_url}")
            print("SCRAPING REAL COMPLETADO!")
            
            driver.quit()
            return True
            
        except Exception as e:
            print(f"Error en navegacion: {e}")
            driver.quit()
            return False
            
    except Exception as e:
        print(f"Error general: {e}")
        return False

if __name__ == "__main__":
    print("PROBANDO SCRAPING REAL DE BANKINTER...")
    success = test_bankinter()
    
    if success:
        print("SUCCESS: Bankinter.com abierto y navegado correctamente")
    else:
        print("FAILED: Error en scraping")
        
    print("Test completado.")