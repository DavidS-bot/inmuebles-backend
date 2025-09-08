#!/usr/bin/env python3
"""
Cliente Bankinter Estable - Método Alternativo
==============================================

Cliente alternativo que usa diferentes estrategias para evitar los crashes
de Chrome y obtener datos de manera más estable.
"""

import time
import json
import csv
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
import os
import tempfile

# Intentar diferentes navegadores/métodos
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    import undetected_chromedriver as uc
    UNDETECTED_CHROME_AVAILABLE = True
except ImportError:
    UNDETECTED_CHROME_AVAILABLE = False

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import requests

class BankinterStableClient:
    """Cliente más estable para Bankinter usando múltiples estrategias"""
    
    def __init__(self):
        self.method = None
        self.driver = None
        self.session = None
        
    def detect_best_method(self) -> str:
        """Detectar el mejor método disponible"""
        
        methods = []
        
        if PLAYWRIGHT_AVAILABLE:
            methods.append(("playwright", "Playwright (más estable)"))
        
        if UNDETECTED_CHROME_AVAILABLE:
            methods.append(("undetected_chrome", "Chrome no detectado"))
        
        methods.append(("selenium_firefox", "Firefox con Selenium"))
        methods.append(("selenium_edge", "Edge con Selenium"))
        methods.append(("requests_only", "Solo requests HTTP"))
        
        print("[INFO] Métodos disponibles:")
        for i, (method_id, description) in enumerate(methods, 1):
            print(f"  {i}. {description}")
        
        return methods[0][0]  # Retornar el mejor disponible
    
    async def connect_with_playwright(self, username: str, password: str) -> Dict[str, Any]:
        """Conectar usando Playwright (más estable que Selenium)"""
        
        if not PLAYWRIGHT_AVAILABLE:
            return {"success": False, "error": "Playwright no disponible"}
        
        try:
            print("[INFO] Iniciando conexión con Playwright...")
            
            async with async_playwright() as p:
                # Usar Firefox en lugar de Chrome
                browser = await p.firefox.launch(
                    headless=False,  # Visible para debugging
                    slow_mo=1000     # Más lento para evitar detección
                )
                
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                
                page = await context.new_page()
                
                # Ir a Bankinter
                print("[INFO] Navegando a Bankinter...")
                await page.goto("https://bankinter.com", wait_until="networkidle")
                
                # Buscar enlace de login
                login_link = await page.query_selector("a[href*='login'], a[href*='acceso']")
                if login_link:
                    await login_link.click()
                    await page.wait_for_load_state("networkidle")
                
                # Introducir credenciales
                await page.fill("input[type='text'], input[name='usuario']", username)
                await page.wait_for_timeout(2000)
                
                # Tomar screenshot para verificar estado
                await page.screenshot(path="playwright_login.png")
                
                # Obtener contenido de la página
                content = await page.content()
                
                await browser.close()
                
                return {
                    "success": True,
                    "method": "playwright",
                    "page_content": content[:1000],  # Primeros 1000 caracteres
                    "screenshot": "playwright_login.png"
                }
                
        except Exception as e:
            return {"success": False, "error": f"Error Playwright: {str(e)}"}
    
    def connect_with_undetected_chrome(self, username: str, password: str) -> Dict[str, Any]:
        """Conectar usando Chrome no detectado"""
        
        if not UNDETECTED_CHROME_AVAILABLE:
            return {"success": False, "error": "Undetected Chrome no disponible"}
        
        try:
            print("[INFO] Iniciando Chrome no detectado...")
            
            # Configurar Chrome no detectado
            options = uc.ChromeOptions()
            options.add_argument("--no-first-run")
            options.add_argument("--no-default-browser-check")
            options.add_argument("--disable-blink-features=AutomationControlled")
            
            driver = uc.Chrome(options=options)
            
            print("[INFO] Navegando a Bankinter...")
            driver.get("https://bankinter.com")
            time.sleep(3)
            
            # Buscar acceso cliente
            login_elements = driver.find_elements(By.PARTIAL_LINK_TEXT, "Acceso")
            if not login_elements:
                login_elements = driver.find_elements(By.PARTIAL_LINK_TEXT, "Login")
            
            if login_elements:
                login_elements[0].click()
                time.sleep(3)
            
            # Introducir usuario
            user_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
            if user_inputs:
                user_inputs[0].send_keys(username)
                time.sleep(2)
            
            # Tomar screenshot
            driver.save_screenshot("undetected_chrome_login.png")
            
            # Obtener contenido
            page_source = driver.page_source
            
            driver.quit()
            
            return {
                "success": True,
                "method": "undetected_chrome",
                "page_content": page_source[:1000],
                "screenshot": "undetected_chrome_login.png"
            }
            
        except Exception as e:
            if 'driver' in locals():
                try:
                    driver.quit()
                except:
                    pass
            return {"success": False, "error": f"Error Chrome no detectado: {str(e)}"}
    
    def connect_with_firefox(self, username: str, password: str) -> Dict[str, Any]:
        """Conectar usando Firefox"""
        
        try:
            print("[INFO] Iniciando Firefox...")
            
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
            from selenium.webdriver.firefox.service import Service as FirefoxService
            
            options = FirefoxOptions()
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")
            
            # Intentar encontrar Firefox
            driver = webdriver.Firefox(options=options)
            
            print("[INFO] Navegando a Bankinter con Firefox...")
            driver.get("https://bankinter.com")
            time.sleep(3)
            
            # Tomar screenshot inicial
            driver.save_screenshot("firefox_initial.png")
            
            # Buscar enlace de acceso
            try:
                login_link = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Acceso"))
                )
                login_link.click()
                time.sleep(3)
            except:
                print("[WARN] No se encontró enlace de acceso")
            
            # Buscar campo de usuario
            try:
                user_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
                )
                user_field.send_keys(username)
                time.sleep(2)
            except:
                print("[WARN] No se encontró campo de usuario")
            
            # Tomar screenshot final
            driver.save_screenshot("firefox_with_user.png")
            
            # Obtener contenido
            page_source = driver.page_source
            
            driver.quit()
            
            return {
                "success": True,
                "method": "firefox",
                "page_content": page_source[:1000],
                "screenshot": "firefox_with_user.png"
            }
            
        except Exception as e:
            if 'driver' in locals():
                try:
                    driver.quit()
                except:
                    pass
            return {"success": False, "error": f"Error Firefox: {str(e)}"}
    
    def connect_with_requests(self, username: str) -> Dict[str, Any]:
        """Método básico usando solo requests"""
        
        try:
            print("[INFO] Conectando con requests HTTP básico...")
            
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            # Obtener página principal
            response = session.get("https://www.bankinter.com")
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "method": "requests",
                    "status_code": response.status_code,
                    "content_length": len(response.text),
                    "headers": dict(response.headers)
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {"success": False, "error": f"Error requests: {str(e)}"}


async def test_all_methods(username: str):
    """Probar todos los métodos disponibles"""
    
    client = BankinterStableClient()
    results = {}
    
    print("=" * 60)
    print("PROBANDO MÉTODOS ALTERNATIVOS PARA BANKINTER")
    print("=" * 60)
    
    # Método 1: Playwright
    if PLAYWRIGHT_AVAILABLE:
        print("\n[TEST 1] Probando Playwright...")
        results['playwright'] = await client.connect_with_playwright(username, "test")
        print(f"Resultado: {'✓ ÉXITO' if results['playwright']['success'] else '✗ FALLO'}")
    
    # Método 2: Chrome no detectado
    if UNDETECTED_CHROME_AVAILABLE:
        print("\n[TEST 2] Probando Chrome no detectado...")
        results['undetected_chrome'] = client.connect_with_undetected_chrome(username, "test")
        print(f"Resultado: {'✓ ÉXITO' if results['undetected_chrome']['success'] else '✗ FALLO'}")
    
    # Método 3: Firefox
    print("\n[TEST 3] Probando Firefox...")
    results['firefox'] = client.connect_with_firefox(username, "test")
    print(f"Resultado: {'✓ ÉXITO' if results['firefox']['success'] else '✗ FALLO'}")
    
    # Método 4: Requests básico
    print("\n[TEST 4] Probando requests básico...")
    results['requests'] = client.connect_with_requests(username)
    print(f"Resultado: {'✓ ÉXITO' if results['requests']['success'] else '✗ FALLO'}")
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE MÉTODOS:")
    print("=" * 60)
    
    successful_methods = []
    
    for method, result in results.items():
        status = "✓ FUNCIONA" if result['success'] else "✗ FALLO"
        error = f" - {result.get('error', '')}" if not result['success'] else ""
        print(f"{method:20} {status}{error}")
        
        if result['success']:
            successful_methods.append(method)
    
    print(f"\nMétodos exitosos: {len(successful_methods)}")
    if successful_methods:
        print(f"Mejor opción: {successful_methods[0]}")
    
    return results, successful_methods


def install_missing_dependencies():
    """Instalar dependencias faltantes"""
    
    print("INSTALACIÓN DE HERRAMIENTAS ALTERNATIVAS")
    print("=" * 50)
    
    if not PLAYWRIGHT_AVAILABLE:
        print("\n[OPCIÓN] Instalar Playwright (recomendado):")
        print("  pip install playwright")
        print("  playwright install firefox")
    
    if not UNDETECTED_CHROME_AVAILABLE:
        print("\n[OPCIÓN] Instalar Chrome no detectado:")
        print("  pip install undetected-chromedriver")
    
    print("\n[OPCIÓN] API PSD2 oficial (mejor solución):")
    print("  Registrarse en https://market.apis-i.redsys.es")
    
    print("\nEjecuta las instalaciones y vuelve a intentar")


if __name__ == "__main__":
    import asyncio
    
    print("CLIENTE BANKINTER ALTERNATIVO")
    print("=" * 40)
    
    # Verificar dependencias
    missing = []
    if not PLAYWRIGHT_AVAILABLE:
        missing.append("playwright")
    if not UNDETECTED_CHROME_AVAILABLE:
        missing.append("undetected-chromedriver")
    
    if missing:
        print(f"Dependencias faltantes: {', '.join(missing)}")
        install_missing_dependencies()
        print("\nInstalando una dependencia básica...")
        os.system("pip install undetected-chromedriver")
    
    # Solicitar username
    username = input("Introduce tu usuario de Bankinter (solo para testing): ").strip()
    if not username:
        username = "75867185"  # Tu usuario conocido
    
    # Ejecutar tests
    asyncio.run(test_all_methods(username))