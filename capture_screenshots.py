#!/usr/bin/env python3
"""
Script para capturar screenshots automáticos de la aplicación
Navega por las páginas principales y captura imágenes
"""

import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

def setup_driver():
    """Configurar el driver de Chrome para screenshots"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Ejecutar sin ventana
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--force-device-scale-factor=1')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error al inicializar Chrome driver: {str(e)}")
        print("Asegúrate de tener Chrome y ChromeDriver instalados")
        return None

def login_to_app(driver, base_url):
    """Hacer login en la aplicación"""
    try:
        # Ir a página de login
        driver.get(f"{base_url}/login")
        
        # Esperar a que aparezcan los campos
        wait = WebDriverWait(driver, 10)
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password_field = driver.find_element(By.NAME, "password")
        
        # Llenar credenciales
        username_field.send_keys("davsanchez21277@gmail.com")
        password_field.send_keys("123456")
        
        # Hacer click en login
        login_button = driver.find_element(By.TYPE, "submit")
        login_button.click()
        
        # Esperar a que se redirija
        wait.until(EC.url_changes(f"{base_url}/login"))
        time.sleep(2)  # Esperar un poco más para que cargue completamente
        
        return True
    except Exception as e:
        print(f"Error en login: {str(e)}")
        return False

def capture_screenshot(driver, url, filename, description):
    """Capturar screenshot de una URL específica"""
    try:
        print(f"Capturando: {description}...")
        driver.get(url)
        
        # Esperar a que cargue la página
        time.sleep(3)
        
        # Scroll hacia abajo y arriba para asegurar que todo esté cargado
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        # Tomar screenshot
        screenshot_path = f"C:\\Users\\davsa\\inmuebles\\backend\\screenshots\\{filename}"
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot guardado: {filename}")
        return True
        
    except Exception as e:
        print(f"Error capturando {description}: {str(e)}")
        return False

def capture_all_screenshots():
    """Capturar screenshots de todas las páginas principales"""
    
    base_url = "http://localhost:3000"
    
    # Lista de páginas a capturar
    pages_to_capture = [
        {
            'url': f"{base_url}/login",
            'filename': '01_login.png',
            'description': 'Página de Login',
            'login_required': False
        },
        {
            'url': f"{base_url}/financial-agent",
            'filename': '02_dashboard_principal.png',
            'description': 'Dashboard Principal - Financial Agent',
            'login_required': True
        },
        {
            'url': f"{base_url}/financial-agent/movements",
            'filename': '03_gestion_movimientos.png',
            'description': 'Gestión de Movimientos Financieros',
            'login_required': True
        },
        {
            'url': f"{base_url}/financial-agent/analytics",
            'filename': '04_analytics_dashboard.png',
            'description': 'Dashboard de Analytics',
            'login_required': True
        },
        {
            'url': f"{base_url}/financial-agent/contracts",
            'filename': '05_gestion_contratos.png',
            'description': 'Gestión de Contratos',
            'login_required': True
        },
        {
            'url': f"{base_url}/financial-agent/rules",
            'filename': '06_reglas_clasificacion.png',
            'description': 'Reglas de Clasificación',
            'login_required': True
        },
        {
            'url': f"{base_url}/financial-agent/integrations",
            'filename': '07_integraciones.png',
            'description': 'Centro de Integraciones',
            'login_required': True
        },
        {
            'url': f"{base_url}/financial-agent/integrations/bankinter",
            'filename': '08_integracion_bankinter.png',
            'description': 'Integración Bankinter',
            'login_required': True
        },
        {
            'url': f"{base_url}/financial-agent/mortgage-calculator",
            'filename': '09_calculadora_hipoteca.png',
            'description': 'Calculadora Hipotecaria',
            'login_required': True
        },
        {
            'url': f"{base_url}/financial-agent/euribor",
            'filename': '10_gestion_euribor.png',
            'description': 'Gestión de Euribor',
            'login_required': True
        },
        {
            'url': f"{base_url}/financial-agent/documents",
            'filename': '11_gestor_documentos.png',
            'description': 'Gestor de Documentos',
            'login_required': True
        },
        {
            'url': f"{base_url}/financial-agent/notifications",
            'filename': '12_notificaciones.png',
            'description': 'Centro de Notificaciones',
            'login_required': True
        },
        {
            'url': f"{base_url}/financial-agent/tax-assistant",
            'filename': '13_asistente_fiscal.png',
            'description': 'Asistente Fiscal',
            'login_required': True
        },
        {
            'url': f"{base_url}/financial-agent/smart-classifier",
            'filename': '14_clasificador_inteligente.png',
            'description': 'Clasificador Inteligente',
            'login_required': True
        }
    ]
    
    # Configurar driver
    driver = setup_driver()
    if not driver:
        return False
    
    try:
        # Hacer login una vez
        print("Realizando login...")
        if not login_to_app(driver, base_url):
            print("No se pudo hacer login")
            return False
        
        print("Login exitoso")
        
        # Capturar screenshots
        successful_captures = 0
        total_pages = len(pages_to_capture)
        
        for page in pages_to_capture:
            if capture_screenshot(driver, page['url'], page['filename'], page['description']):
                successful_captures += 1
            time.sleep(2)  # Pausa entre capturas
        
        print(f"\nResumen de capturas:")
        print(f"Exitosas: {successful_captures}")
        print(f"Fallidas: {total_pages - successful_captures}")
        print(f"Screenshots guardados en: C:\\Users\\davsa\\inmuebles\\backend\\screenshots\\")
        
        return successful_captures == total_pages
        
    except Exception as e:
        print(f"Error general: {str(e)}")
        return False
    finally:
        driver.quit()

def capture_property_specific_pages():
    """Capturar screenshots de páginas específicas de propiedades"""
    
    base_url = "http://localhost:3000"
    property_id = "1"  # Usar ID de propiedad existente
    
    property_pages = [
        {
            'url': f"{base_url}/financial-agent/property/{property_id}",
            'filename': f'15_propiedad_vista_general.png',
            'description': f'Vista General de Propiedad ID {property_id}'
        },
        {
            'url': f"{base_url}/financial-agent/property/{property_id}/reports",
            'filename': f'16_informes_propiedad.png',
            'description': f'Informes Financieros - Propiedad ID {property_id}'
        },
        {
            'url': f"{base_url}/financial-agent/property/{property_id}/mortgage",
            'filename': f'17_hipoteca_propiedad.png',
            'description': f'Gestión Hipotecaria - Propiedad ID {property_id}'
        },
        {
            'url': f"{base_url}/financial-agent/property/{property_id}/rules",
            'filename': f'18_reglas_propiedad.png',
            'description': f'Reglas Específicas - Propiedad ID {property_id}'
        }
    ]
    
    driver = setup_driver()
    if not driver:
        return False
    
    try:
        # Login
        if not login_to_app(driver, base_url):
            return False
        
        # Capturar páginas de propiedad
        for page in property_pages:
            capture_screenshot(driver, page['url'], page['filename'], page['description'])
            time.sleep(2)
        
        return True
        
    except Exception as e:
        print(f"Error capturando páginas de propiedad: {str(e)}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    print("Iniciando captura de screenshots de la aplicacion...")
    print("Asegurate de que la aplicacion este corriendo en http://localhost:3000")
    
    # Verificar si la aplicación está corriendo
    try:
        import requests
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code != 200:
            print("La aplicacion no parece estar disponible en localhost:3000")
            exit(1)
    except:
        print("No se puede conectar a localhost:3000")
        print("Ejecuta 'npm run dev' en la carpeta inmuebles-web")
        exit(1)
    
    print("Aplicacion detectada, iniciando capturas...")
    
    # Capturar páginas principales
    if capture_all_screenshots():
        print("Capturas principales completadas")
    else:
        print("Algunas capturas principales fallaron")
    
    # Capturar páginas de propiedad específicas
    print("\nCapturando paginas especificas de propiedades...")
    if capture_property_specific_pages():
        print("Capturas de propiedades completadas")
    else:
        print("Capturas de propiedades fallaron")
    
    print("\nProceso de capturas completado!")
    print("Revisa la carpeta 'screenshots' para ver las imagenes capturadas")