#!/usr/bin/env python3
"""
Navegar paso a paso al área de movimientos después del login
"""

import asyncio
import logging
from datetime import date
from app.services.bankinter_scraper_v2 import BankinterScraperV2
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO)

async def navigate_to_movements():
    """Navegar paso a paso a movimientos"""
    
    username = "75867185"
    password = "Motoreta123$"
    
    print("NAVEGACION PASO A PASO A MOVIMIENTOS")
    print("=" * 60)
    
    scraper = None
    try:
        scraper = BankinterScraperV2(username=username, password=password)
        
        print("\n[1/6] Realizando login...")
        scraper.setup_driver()
        
        login_ok = await scraper.login()
        if not login_ok:
            print("ERROR: Login fallido")
            return
        
        print("OK - Login exitoso")
        await asyncio.sleep(5)
        
        current_url = scraper.driver.current_url
        print(f"URL después del login: {current_url}")
        
        # Screenshot del estado inicial
        scraper.driver.save_screenshot("step1_after_login.png")
        
        print("\n[2/6] Buscando navegación a cuentas...")
        
        # Buscar enlaces que lleven a cuentas/movimientos
        navigation_attempts = [
            # Buscar por texto
            ("//a[contains(text(), 'Cuentas')]", "Enlace 'Cuentas'"),
            ("//a[contains(text(), 'Movimientos')]", "Enlace 'Movimientos'"),
            ("//a[contains(text(), 'Extractos')]", "Enlace 'Extractos'"),
            ("//a[contains(text(), 'Consultas')]", "Enlace 'Consultas'"),
            
            # Buscar por href
            ("//a[contains(@href, 'cuentas')]", "Link con 'cuentas'"),
            ("//a[contains(@href, 'movimientos')]", "Link con 'movimientos'"),
            ("//a[contains(@href, 'extracto')]", "Link con 'extracto'"),
            
            # Menús y botones
            (".menu-item a", "Items de menú"),
            ("button[onclick*='cuenta']", "Botones de cuenta"),
            (".nav-link", "Enlaces de navegación"),
        ]
        
        step_found = False
        for selector, description in navigation_attempts:
            try:
                print(f"  Probando: {description}")
                
                if selector.startswith("//"):
                    elements = scraper.driver.find_elements(By.XPATH, selector)
                else:
                    elements = scraper.driver.find_elements(By.CSS_SELECTOR, selector)
                
                if elements:
                    print(f"    Encontrados: {len(elements)} elementos")
                    
                    for i, element in enumerate(elements[:3]):  # Probar los primeros 3
                        try:
                            if element.is_displayed():
                                text = element.text.strip()
                                href = element.get_attribute('href') or ""
                                
                                print(f"    {i+1}. Texto: '{text[:30]}' | Href: {href[:50]}")
                                
                                # Hacer clic
                                element.click()
                                await asyncio.sleep(4)
                                
                                new_url = scraper.driver.current_url
                                print(f"    -> Nueva URL: {new_url}")
                                
                                # Si navegamos exitosamente, continuar
                                if new_url != current_url and "bancaonline.bankinter.com" in new_url:
                                    current_url = new_url
                                    step_found = True
                                    scraper.driver.save_screenshot(f"step2_navigation_{i}.png")
                                    break
                                    
                        except Exception as e:
                            print(f"    Error con elemento {i+1}: {e}")
                            continue
                
                if step_found:
                    break
                    
            except Exception as e:
                print(f"  Error con {description}: {e}")
                continue
        
        if not step_found:
            print("  No se encontró navegación directa, intentando URLs conocidas...")
            
            # Intentar URLs secuenciales
            sequential_urls = [
                "https://bancaonline.bankinter.com/gestion/posicion.xhtml",
                "https://bancaonline.bankinter.com/gestion/cuentas.xhtml",
            ]
            
            for url in sequential_urls:
                try:
                    print(f"    Intentando: {url}")
                    scraper.driver.get(url)
                    await asyncio.sleep(4)
                    
                    if scraper.driver.current_url != url:
                        print(f"    Redirigido a: {scraper.driver.current_url}")
                    else:
                        print(f"    Exitoso en: {url}")
                        current_url = url
                        step_found = True
                        break
                        
                except Exception as e:
                    print(f"    Error: {e}")
                    continue
        
        print(f"\nURL actual después de navegación: {current_url}")
        scraper.driver.save_screenshot("step3_after_navigation.png")
        
        print("\n[3/6] Buscando acceso específico a movimientos...")
        
        # Ahora buscar enlaces específicos a movimientos desde donde estemos
        movement_selectors = [
            ("//a[contains(@href, 'movimientos_cuenta')]", "Link directo a movimientos_cuenta"),
            ("//a[contains(text(), 'Movimientos de cuenta')]", "Texto 'Movimientos de cuenta'"),
            ("//a[contains(text(), 'Ver movimientos')]", "Texto 'Ver movimientos'"),
            ("//button[contains(text(), 'Movimientos')]", "Botón 'Movimientos'"),
            (".account-movements a", "Enlaces de movimientos de cuenta"),
        ]
        
        movements_found = False
        for selector, description in movement_selectors:
            try:
                print(f"  Buscando: {description}")
                
                if selector.startswith("//"):
                    elements = scraper.driver.find_elements(By.XPATH, selector)
                else:
                    elements = scraper.driver.find_elements(By.CSS_SELECTOR, selector)
                
                if elements:
                    print(f"    Encontrados: {len(elements)}")
                    
                    for element in elements[:2]:
                        try:
                            if element.is_displayed():
                                text = element.text.strip()
                                href = element.get_attribute('href') or ""
                                print(f"    Texto: '{text}' | Href: {href}")
                                
                                element.click()
                                await asyncio.sleep(5)
                                
                                new_url = scraper.driver.current_url
                                print(f"    -> URL después del clic: {new_url}")
                                
                                # Verificar si llegamos a movimientos
                                if "movimientos" in new_url.lower():
                                    movements_found = True
                                    scraper.driver.save_screenshot("step4_movements_page.png")
                                    break
                                    
                        except Exception as e:
                            print(f"    Error: {e}")
                            continue
                
                if movements_found:
                    break
                    
            except Exception as e:
                print(f"  Error con {description}: {e}")
                continue
        
        if not movements_found:
            print("  Intentando URL directa de movimientos con cookies de sesión...")
            try:
                target_url = "https://bancaonline.bankinter.com/extracto/secure/movimientos_cuenta.xhtml?INDEX_CTA=1&IND=C&TIPO=N"
                scraper.driver.get(target_url)
                await asyncio.sleep(5)
                
                final_url = scraper.driver.current_url
                print(f"    URL final: {final_url}")
                
                if "movimientos" in final_url or "extracto" in final_url:
                    movements_found = True
                    
            except Exception as e:
                print(f"    Error con URL directa: {e}")
        
        current_url = scraper.driver.current_url
        print(f"\nURL final: {current_url}")
        
        print("\n[4/6] Analizando página de movimientos...")
        
        # Screenshot de la página final
        scraper.driver.save_screenshot("step5_final_movements_page.png")
        
        # Análisis de contenido
        page_source = scraper.driver.page_source
        page_title = scraper.driver.title
        
        print(f"Título: {page_title}")
        print(f"Tamaño: {len(page_source)} caracteres")
        
        # Buscar indicadores de movimientos
        indicators = ['agosto', 'movimiento', 'fecha', 'importe', 'saldo', 'cuenta']
        found_indicators = {}
        
        for indicator in indicators:
            count = page_source.lower().count(indicator)
            found_indicators[indicator] = count
        
        print(f"Indicadores: {found_indicators}")
        
        # Buscar fechas de agosto específicamente
        import re
        agosto_patterns = [
            r'08[/-]2025',
            r'2025[/-]08',
            r'ago\w*\s*2025',
            r'agosto\s*2025'
        ]
        
        agosto_matches = []
        for pattern in agosto_patterns:
            matches = re.findall(pattern, page_source, re.IGNORECASE)
            agosto_matches.extend(matches)
        
        print(f"Referencias a agosto 2025: {len(agosto_matches)}")
        if agosto_matches:
            print(f"  Ejemplos: {agosto_matches[:5]}")
        
        print("\n[5/6] Intentando extracción de datos...")
        
        # Usar el método existente
        movimientos = scraper._extract_transactions_from_current_page()
        
        if movimientos:
            print(f"Movimientos extraídos: {len(movimientos)}")
            
            agosto_2025 = [m for m in movimientos if m.date.year == 2025 and m.date.month == 8]
            print(f"Agosto 2025: {len(agosto_2025)}")
            
            if agosto_2025:
                print(f"\n=== MOVIMIENTOS DE AGOSTO 2025 ENCONTRADOS ===")
                for i, mov in enumerate(agosto_2025, 1):
                    fecha = mov.date.strftime('%d/%m/%Y')
                    desc = mov.description[:50]
                    print(f"{i:2d}. {fecha} | {desc:50} | {mov.amount:8.2f}EUR")
                
                total = sum(m.amount for m in agosto_2025)
                print(f"\nTOTAL AGOSTO 2025: {total:.2f}EUR")
                
                # Exportar
                csv_file = await scraper.export_to_csv(agosto_2025, "movimientos_agosto_real.csv")
                print(f"Exportado: {csv_file}")
                
                return True
            
        else:
            print("Sin movimientos extraídos con método actual")
            
            print("\n[6/6] Análisis manual de la estructura...")
            
            # Buscar tablas
            tables = scraper.driver.find_elements(By.TAG_NAME, "table")
            print(f"Tablas: {len(tables)}")
            
            for i, table in enumerate(tables[:3]):
                try:
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    print(f"  Tabla {i+1}: {len(rows)} filas")
                    
                    # Analizar primeras filas
                    for j, row in enumerate(rows[:3]):
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if cells:
                            row_text = " | ".join([cell.text.strip()[:20] for cell in cells[:5]])
                            print(f"    Fila {j+1}: {row_text}")
                            
                except Exception as e:
                    print(f"  Error analizando tabla {i+1}: {e}")
            
            # Buscar divs con estructura de movimientos
            movement_divs = scraper.driver.find_elements(By.CSS_SELECTOR, 
                "div[class*='movement'], div[class*='transaction'], div[class*='row']")
            
            print(f"Divs de movimientos potenciales: {len(movement_divs)}")
            
            # Si encontramos estructuras pero no datos, hay un problema de parsing
            if tables or movement_divs:
                print("PROBLEMA: Hay estructura de datos pero no se extraen")
                print("El método _extract_transactions_from_current_page necesita ajustes")
        
        return False
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False
        
    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    try:
        resultado = asyncio.run(navigate_to_movements())
        
        if resultado:
            print(f"\n" + "="*60)
            print(f"EXITO: MOVIMIENTOS DE AGOSTO 2025 ENCONTRADOS")
            print(f"="*60)
        else:
            print(f"\n" + "="*60)
            print(f"INFO: NAVEGACION COMPLETA - AJUSTAR EXTRACCION")
            print(f"Llegamos a la página correcta, falta mejorar el parser")
            print(f"="*60)
            
    except Exception as e:
        print(f"\nERROR: {e}")