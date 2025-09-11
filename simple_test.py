#!/usr/bin/env python3
"""
Test simple del scraping de Bankinter
"""
def test_bankinter_scraping():
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager
        import time
        
        print("INICIANDO TEST DE BANKINTER...")
        
        options = Options()
        options.add_argument("--headless")  # Headless para test rapido
        options.add_argument("--no-sandbox") 
        options.add_argument("--disable-dev-shm-usage")
        
        from selenium.webdriver.chrome.service import Service
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        print("Navegando a Bankinter...")
        driver.get("https://www.bankinter.com")
        time.sleep(3)
        
        print("Buscando ACCESO CLIENTES...")
        access_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'ACCESO CLIENTES')]"))
        )
        print("ACCESO CLIENTES encontrado!")
        
        driver.quit()
        
        return {
            "success": True,
            "message": "Test basico exitoso - navegacion y ACCESO CLIENTES OK"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    result = test_bankinter_scraping()
    if result["success"]:
        print("SUCCESS:", result["message"])
    else:
        print("ERROR:", result["error"])