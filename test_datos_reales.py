#!/usr/bin/env python3
"""
Test específico para obtener datos bancarios reales
Navegación manual por la interfaz de usuario real
"""

import asyncio
import logging
import time
from datetime import date, datetime
from app.services.bankinter_scraper_v2 import BankinterScraperV2
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def buscar_datos_reales():
    """Búsqueda exhaustiva de datos bancarios reales"""
    
    username = "75867185"
    password = "Motoreta123$"
    
    print("BUSQUEDA DE DATOS BANCARIOS REALES")
    print("=" * 60)
    print(f"Usuario: {username}")
    print("Estrategia: Navegacion manual por toda la interfaz")
    
    scraper = None
    try:
        scraper = BankinterScraperV2(username=username, password=password)
        
        print("\n[1/6] Configurando navegador...")
        scraper.setup_driver()
        
        print("\n[2/6] Realizando login...")
        login_ok = await scraper.login()
        if not login_ok:
            print("[ERROR] Login fallido")
            return
        
        print("[OK] Login exitoso - Dentro del sistema de Bankinter")
        
        # Esperar más tiempo para asegurar carga completa
        print("\n[3/6] Esperando carga completa del sistema...")
        await asyncio.sleep(8)
        
        # Tomar screenshot de la página principal
        scraper.driver.save_screenshot("pagina_principal_post_login.png")
        print("Screenshot guardado: pagina_principal_post_login.png")
        
        print("\n[4/6] EXPLORANDO INTERFAZ REAL...")
        
        # Estrategia 1: Buscar todos los enlaces disponibles
        print("\n--- Estrategia 1: Analizando TODOS los enlaces ---")
        enlaces = await _analizar_enlaces(scraper)
        
        # Estrategia 2: Buscar menús de navegación específicos
        print("\n--- Estrategia 2: Buscando menús específicos ---")
        await _buscar_menus_bancarios(scraper)
        
        # Estrategia 3: Intentar URLs directas conocidas
        print("\n--- Estrategia 3: URLs directas del área cliente ---")
        await _probar_urls_directas(scraper)
        
        # Estrategia 4: JavaScript para encontrar elementos ocultos
        print("\n--- Estrategia 4: Búsqueda con JavaScript ---")
        await _buscar_con_javascript(scraper)
        
        print("\n[5/6] EXTRAYENDO DATOS DE TODAS LAS PÁGINAS VISITADAS...")
        
        # Recopilar todos los datos encontrados
        todos_los_datos = []
        
        # Extraer de la página actual
        datos_actuales = scraper._extract_transactions_from_current_page()
        if datos_actuales:
            todos_los_datos.extend(datos_actuales)
            print(f"Datos de pagina actual: {len(datos_actuales)}")
        
        print(f"\n[6/6] RESULTADO FINAL:")
        print(f"Total datos encontrados: {len(todos_los_datos)}")
        
        if todos_los_datos:
            print(f"\n=== DATOS ENCONTRADOS ===")
            
            # Filtrar solo agosto 2025 (mes actual)
            agosto_2025 = [d for d in todos_los_datos if d.date.year == 2025 and d.date.month == 8]
            
            print(f"Total general: {len(todos_los_datos)}")
            print(f"Agosto 2025: {len(agosto_2025)}")
            
            if agosto_2025:
                print(f"\n--- MOVIMIENTOS DE AGOSTO 2025 ---")
                for i, mov in enumerate(agosto_2025, 1):
                    print(f"{i}. {mov.date.strftime('%d/%m/%Y')} - {mov.description[:60]} - {mov.amount:.2f}EUR")
            
            # Mostrar todos los datos sin filtro
            print(f"\n--- TODOS LOS DATOS (SIN FILTRO) ---")
            for i, mov in enumerate(todos_los_datos, 1):
                print(f"{i:2d}. {mov.date.strftime('%d/%m/%Y')} - {mov.description[:50]:50} - {mov.amount:8.2f}EUR")
            
            # Exportar todo
            await scraper.export_to_csv(todos_los_datos, "datos_reales_bankinter.csv")
            print(f"\nTodos los datos exportados a: datos_reales_bankinter.csv")
            
        else:
            print("No se encontraron datos bancarios")
            
            # Información de debug detallada
            print(f"\n=== DEBUG DETALLADO ===")
            current_url = scraper.driver.current_url
            print(f"URL actual: {current_url}")
            
            # Analizar contenido de la página
            page_source = scraper.driver.page_source
            print(f"Tamaño de página: {len(page_source)} caracteres")
            
            # Buscar palabras clave bancarias
            keywords = ['saldo', 'balance', 'cuenta', 'movimiento', 'transaccion', 'operacion', 'transferencia']
            found_keywords = []
            for keyword in keywords:
                if keyword in page_source.lower():
                    found_keywords.append(keyword)
            
            print(f"Palabras clave bancarias encontradas: {found_keywords}")
            
            # Buscar formularios
            forms = scraper.driver.find_elements(By.TAG_NAME, "form")
            print(f"Formularios en la página: {len(forms)}")
            
            # Buscar inputs que puedan ser de fechas
            date_inputs = scraper.driver.find_elements(By.CSS_SELECTOR, "input[type='date'], input[placeholder*='fecha']")
            print(f"Campos de fecha encontrados: {len(date_inputs)}")
            
        return len(todos_los_datos) > 0
        
    except Exception as e:
        print(f"ERROR: {e}")
        logger.error(f"Error buscando datos reales: {e}")
        return False
        
    finally:
        if scraper:
            print(f"\nCerrando navegador...")
            scraper.close()

async def _analizar_enlaces(scraper):
    """Analizar todos los enlaces de la página"""
    try:
        enlaces = scraper.driver.find_elements(By.TAG_NAME, "a")
        enlaces_bancarios = []
        
        print(f"Total enlaces encontrados: {len(enlaces)}")
        
        for enlace in enlaces:
            try:
                if enlace.is_displayed():
                    texto = enlace.text.strip().lower()
                    href = enlace.get_attribute('href') or ""
                    
                    # Buscar enlaces que parezcan bancarios
                    keywords_bancarios = ['cuenta', 'movimiento', 'saldo', 'transaccion', 'posicion', 'consulta', 'operacion']
                    
                    if any(kw in texto for kw in keywords_bancarios) or any(kw in href.lower() for kw in keywords_bancarios):
                        enlaces_bancarios.append({
                            'texto': enlace.text.strip()[:50],
                            'href': href,
                            'elemento': enlace
                        })
                        
            except:
                continue
        
        print(f"Enlaces bancarios potenciales: {len(enlaces_bancarios)}")
        
        # Intentar hacer clic en los enlaces más prometedores
        for i, enlace_info in enumerate(enlaces_bancarios[:5], 1):  # Solo los primeros 5
            try:
                print(f"  {i}. Intentando: {enlace_info['texto']}")
                
                # Hacer clic en el enlace
                enlace_info['elemento'].click()
                await asyncio.sleep(3)
                
                # Verificar si cambió la URL
                new_url = scraper.driver.current_url
                print(f"     Nueva URL: {new_url}")
                
                # Tomar screenshot
                scraper.driver.save_screenshot(f"enlace_{i}_{int(time.time())}.png")
                
                # Extraer datos de esta página
                datos_pagina = scraper._extract_transactions_from_current_page()
                if datos_pagina:
                    print(f"     ¡DATOS ENCONTRADOS! {len(datos_pagina)} elementos")
                    return datos_pagina
                
            except Exception as e:
                print(f"     Error con enlace {i}: {e}")
                continue
        
        return []
        
    except Exception as e:
        logger.error(f"Error analizando enlaces: {e}")
        return []

async def _buscar_menus_bancarios(scraper):
    """Buscar menús específicos de banca"""
    try:
        # Selectores de menús típicos
        menu_selectors = [
            "nav", ".navigation", ".menu", ".sidebar", 
            ".header-menu", ".main-menu", ".user-menu",
            "[role='navigation']", ".nav-list", ".menu-list"
        ]
        
        for selector in menu_selectors:
            try:
                menus = scraper.driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"Menús encontrados con {selector}: {len(menus)}")
                
                for menu in menus:
                    if menu.is_displayed():
                        # Buscar enlaces dentro del menú
                        enlaces = menu.find_elements(By.TAG_NAME, "a")
                        for enlace in enlaces:
                            texto = enlace.text.strip().lower()
                            if any(kw in texto for kw in ['cuenta', 'movimiento', 'consulta', 'posicion']):
                                print(f"  Enlace de menú encontrado: {enlace.text.strip()}")
                                try:
                                    enlace.click()
                                    await asyncio.sleep(2)
                                    
                                    # Verificar si llegamos a datos bancarios
                                    datos = scraper._extract_transactions_from_current_page()
                                    if datos:
                                        print(f"  ¡DATOS DE MENÚ! {len(datos)} elementos")
                                        return datos
                                        
                                except:
                                    continue
                            
            except Exception as e:
                print(f"Error con selector de menú {selector}: {e}")
                continue
                
        return []
        
    except Exception as e:
        logger.error(f"Error buscando menús: {e}")
        return []

async def _probar_urls_directas(scraper):
    """Probar URLs directas conocidas del área de cliente"""
    try:
        current_url = scraper.driver.current_url
        base_url = "/".join(current_url.split("/")[:3])
        
        # URLs típicas de banca online
        urls_directas = [
            f"{base_url}/gestion/posicion",
            f"{base_url}/gestion/cuentas-corrientes",
            f"{base_url}/gestion/movimientos",
            f"{base_url}/gestion/consultas",
            f"{base_url}/gestion/saldos",
            f"{base_url}/gestion/extractos",
            f"{base_url}/gestion/operaciones",
            f"{base_url}/banca/posicion",
            f"{base_url}/banca/cuentas",
            f"{base_url}/banca/movimientos",
            f"{base_url}/cliente/cuentas",
            f"{base_url}/cliente/posicion",
        ]
        
        for url in urls_directas:
            try:
                print(f"Probando URL directa: {url}")
                scraper.driver.get(url)
                await asyncio.sleep(3)
                
                final_url = scraper.driver.current_url
                print(f"  Resultado: {final_url}")
                
                # Verificar si no es error 404
                if "notfound" not in final_url.lower() and "error" not in final_url.lower():
                    datos = scraper._extract_transactions_from_current_page()
                    if datos:
                        print(f"  ¡DATOS EN URL DIRECTA! {len(datos)} elementos")
                        return datos
                        
            except Exception as e:
                print(f"  Error con URL {url}: {e}")
                continue
        
        return []
        
    except Exception as e:
        logger.error(f"Error probando URLs directas: {e}")
        return []

async def _buscar_con_javascript(scraper):
    """Usar JavaScript para encontrar elementos ocultos"""
    try:
        # Scripts de JavaScript para buscar datos
        js_scripts = [
            # Buscar texto con patrones de dinero
            """
            return Array.from(document.querySelectorAll('*'))
                .filter(el => el.textContent && /\\d+[.,]\\d{2}.*€/.test(el.textContent))
                .map(el => el.textContent.trim())
                .slice(0, 20);
            """,
            
            # Buscar elementos con fechas
            """
            return Array.from(document.querySelectorAll('*'))
                .filter(el => el.textContent && /\\d{1,2}[/-]\\d{1,2}[/-]\\d{4}/.test(el.textContent))
                .map(el => el.textContent.trim())
                .slice(0, 10);
            """,
            
            # Buscar formularios ocultos
            """
            return Array.from(document.querySelectorAll('form'))
                .map(form => ({
                    action: form.action,
                    method: form.method,
                    inputs: form.querySelectorAll('input').length
                }));
            """,
        ]
        
        for i, script in enumerate(js_scripts, 1):
            try:
                resultado = scraper.driver.execute_script(script)
                print(f"JavaScript {i}: {len(resultado) if isinstance(resultado, list) else 1} resultados")
                
                if resultado:
                    for j, res in enumerate(resultado[:5] if isinstance(resultado, list) else [resultado]):
                        print(f"  {j+1}. {str(res)[:100]}")
                        
            except Exception as e:
                print(f"Error con JavaScript {i}: {e}")
                continue
        
        return []
        
    except Exception as e:
        logger.error(f"Error con JavaScript: {e}")
        return []

if __name__ == "__main__":
    try:
        resultado = asyncio.run(buscar_datos_reales())
        
        if resultado:
            print(f"\n" + "="*60)
            print(f"[EXITO] DATOS BANCARIOS REALES ENCONTRADOS")
            print(f"="*60)
        else:
            print(f"\n" + "="*60)
            print(f"[INFO] EXPLORACION COMPLETA TERMINADA")
            print(f"Se accedio correctamente pero no se encontraron movimientos reales")
            print(f"Posibles causas:")
            print(f"- Cuenta sin movimientos en el periodo")
            print(f"- Datos en otra seccion no explorada")
            print(f"- Bankinter requiere pasos adicionales")
            print(f"="*60)
            
    except KeyboardInterrupt:
        print(f"\n[CANCELADO] Busqueda interrumpida por usuario")
    except Exception as e:
        print(f"\n[ERROR] Error fatal: {e}")