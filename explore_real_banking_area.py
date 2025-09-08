#!/usr/bin/env python3
"""
Explorador específico del área real de banca online de Bankinter
Se mantiene en bancaonline.bankinter.com después del login
"""

import asyncio
import logging
import time
from datetime import date
from app.services.bankinter_scraper_v2 import BankinterScraperV2
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def explore_real_banking():
    """Explorar el área real de banca online"""
    
    username = "75867185" 
    password = "Motoreta123$"
    
    print("EXPLORACION DEL AREA REAL DE BANCA ONLINE")
    print("=" * 60)
    print("Objetivo: Encontrar movimientos reales en bancaonline.bankinter.com")
    
    scraper = None
    try:
        scraper = BankinterScraperV2(username=username, password=password)
        
        print("\n[1/5] Configurando y realizando login...")
        scraper.setup_driver()
        
        login_ok = await scraper.login()
        if not login_ok:
            print("[ERROR] Login fallido")
            return
        
        print("[OK] Login exitoso - Dentro del area bancaria")
        
        # Esperar a que la página cargue completamente
        await asyncio.sleep(5)
        
        current_url = scraper.driver.current_url
        print(f"URL actual después del login: {current_url}")
        
        # Tomar screenshot del estado post-login
        scraper.driver.save_screenshot("post_login_real_area.png")
        
        print("\n[2/5] EXPLORANDO AREA BANCARIA REAL...")
        
        # Solo trabajar en el dominio seguro bancaonline.bankinter.com
        if "bancaonline.bankinter.com" not in current_url:
            print("ERROR: No estamos en el area bancaria segura")
            return
        
        # Estrategia 1: Buscar el menú principal de la banca online
        print("\n--- Buscando menu principal ---")
        await _buscar_menu_principal(scraper)
        
        # Estrategia 2: Buscar enlaces específicos de cuentas y movimientos
        print("\n--- Buscando enlaces de cuentas ---")
        await _buscar_enlaces_cuentas(scraper)
        
        # Estrategia 3: Probar URLs específicas del área bancaria
        print("\n--- Probando URLs bancarias específicas ---")
        await _probar_urls_bancarias(scraper)
        
        # Estrategia 4: Explorar todos los frames/iframes
        print("\n--- Explorando frames y popups ---")
        await _explorar_frames(scraper)
        
        print("\n[3/5] BUSQUEDA EXHAUSTIVA DE MOVIMIENTOS...")
        todos_los_movimientos = []
        
        # Recopilar datos de todas las páginas visitadas
        try:
            movimientos = scraper._extract_transactions_from_current_page()
            if movimientos:
                todos_los_movimientos.extend(movimientos)
                print(f"Movimientos encontrados: {len(movimientos)}")
        except Exception as e:
            print(f"Error extrayendo datos: {e}")
        
        print(f"\n[4/5] RESULTADOS:")
        print(f"Total movimientos encontrados: {len(todos_los_movimientos)}")
        
        if todos_los_movimientos:
            # Filtrar agosto 2025
            agosto_2025 = [m for m in todos_los_movimientos if m.date.year == 2025 and m.date.month == 8]
            
            print(f"\n=== MOVIMIENTOS ENCONTRADOS ===")
            print(f"Total: {len(todos_los_movimientos)}")
            print(f"Agosto 2025: {len(agosto_2025)}")
            
            if agosto_2025:
                print(f"\n--- MOVIMIENTOS DE AGOSTO 2025 ---")
                for i, mov in enumerate(agosto_2025, 1):
                    print(f"{i}. {mov.date.strftime('%d/%m/%Y')} - {mov.description} - {mov.amount:.2f}EUR")
            
            # Mostrar todos
            print(f"\n--- TODOS LOS MOVIMIENTOS ---")
            for i, mov in enumerate(todos_los_movimientos[:20], 1):  # Primeros 20
                print(f"{i}. {mov.date.strftime('%d/%m/%Y')} - {mov.description[:50]} - {mov.amount:.2f}EUR")
                
            if len(todos_los_movimientos) > 20:
                print(f"... y {len(todos_los_movimientos) - 20} movimientos más")
        
        else:
            print("[AVISO] No se encontraron movimientos bancarios reales")
            
            # Debug detallado
            print(f"\n=== INFORMACION DE DEBUG ===")
            print(f"URL final: {scraper.driver.current_url}")
            
            # Análisis del contenido
            page_source = scraper.driver.page_source
            print(f"Tamaño página: {len(page_source)} caracteres")
            
            # Buscar indicadores bancarios
            indicators = ['saldo', 'cuenta corriente', 'extracto', 'movimiento', 'operacion']
            found_indicators = []
            for indicator in indicators:
                if indicator in page_source.lower():
                    count = page_source.lower().count(indicator)
                    found_indicators.append(f"{indicator}({count})")
            
            print(f"Indicadores bancarios: {', '.join(found_indicators)}")
            
            # Buscar formularios de consulta
            forms = scraper.driver.find_elements(By.TAG_NAME, "form")
            print(f"Formularios encontrados: {len(forms)}")
            
            for i, form in enumerate(forms[:3]):  # Primeros 3 formularios
                try:
                    inputs = form.find_elements(By.TAG_NAME, "input")
                    selects = form.find_elements(By.TAG_NAME, "select") 
                    print(f"  Formulario {i+1}: {len(inputs)} inputs, {len(selects)} selects")
                except:
                    pass
        
        print(f"\n[5/5] MAPA COMPLETO DE NAVEGACION")
        await _generar_mapa_navegacion(scraper)
        
        return len(todos_los_movimientos) > 0
        
    except Exception as e:
        print(f"ERROR: {e}")
        logger.error(f"Error explorando area real: {e}")
        return False
        
    finally:
        if scraper:
            print(f"\nCerrando navegador...")
            scraper.close()

async def _buscar_menu_principal(scraper):
    """Buscar y analizar el menú principal"""
    try:
        # Selectores típicos de menús bancarios
        menu_selectors = [
            "nav", ".nav", ".navigation", ".menu", ".main-menu",
            ".sidebar", ".header", ".top-menu", "#menu",
            "[role='navigation']", ".menu-container"
        ]
        
        menus_encontrados = 0
        
        for selector in menu_selectors:
            try:
                elementos = scraper.driver.find_elements(By.CSS_SELECTOR, selector)
                if elementos:
                    menus_encontrados += len(elementos)
                    print(f"  Menu con {selector}: {len(elementos)} elementos")
                    
                    # Analizar enlaces en cada menú
                    for menu in elementos[:2]:  # Solo los primeros 2
                        if menu.is_displayed():
                            enlaces = menu.find_elements(By.TAG_NAME, "a")
                            for enlace in enlaces[:5]:  # Primeros 5 enlaces
                                try:
                                    texto = enlace.text.strip().lower()
                                    href = enlace.get_attribute('href') or ""
                                    
                                    # Buscar enlaces bancarios
                                    keywords = ['cuenta', 'movimiento', 'extracto', 'consulta', 'posicion']
                                    if any(kw in texto for kw in keywords):
                                        print(f"    Enlace bancario: '{enlace.text.strip()[:30]}' -> {href[:50]}")
                                        
                                        # Intentar hacer clic
                                        try:
                                            enlace.click()
                                            await asyncio.sleep(2)
                                            
                                            new_url = scraper.driver.current_url
                                            if "bancaonline.bankinter.com" in new_url:
                                                print(f"      OK: Navegado a {new_url}")
                                                
                                                # Verificar si hay datos aquí
                                                movs = scraper._extract_transactions_from_current_page()
                                                if movs:
                                                    print(f"      ¡DATOS! {len(movs)} movimientos")
                                                    return movs
                                            else:
                                                print(f"      Redirigido fuera del area bancaria: {new_url}")
                                                
                                        except Exception as e:
                                            print(f"      Error haciendo clic: {e}")
                                
                                except:
                                    continue
            except:
                continue
        
        print(f"Total menus analizados: {menus_encontrados}")
        return []
        
    except Exception as e:
        print(f"Error buscando menu principal: {e}")
        return []

async def _buscar_enlaces_cuentas(scraper):
    """Buscar enlaces específicos relacionados con cuentas"""
    try:
        # Texto de enlaces típicos en banca online
        link_texts = [
            'cuentas', 'mis cuentas', 'cuenta corriente', 'saldo',
            'movimientos', 'extractos', 'consultas', 'posicion global',
            'operaciones', 'transferencias', 'historico'
        ]
        
        enlaces_probados = 0
        
        for text in link_texts:
            try:
                # Buscar por texto exacto y parcial
                xpath_selectors = [
                    f"//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text}')]",
                    f"//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text}')]",
                    f"//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text}')]//ancestor::a"
                ]
                
                for selector in xpath_selectors:
                    elementos = scraper.driver.find_elements(By.XPATH, selector)
                    
                    for elemento in elementos[:2]:  # Máximo 2 por selector
                        if elemento.is_displayed():
                            print(f"  Probando enlace: '{elemento.text.strip()[:30]}'")
                            enlaces_probados += 1
                            
                            try:
                                elemento.click()
                                await asyncio.sleep(3)
                                
                                new_url = scraper.driver.current_url
                                print(f"    Navegado a: {new_url}")
                                
                                # Solo continuar si seguimos en el área bancaria
                                if "bancaonline.bankinter.com" in new_url:
                                    # Buscar movimientos
                                    movs = scraper._extract_transactions_from_current_page()
                                    if movs:
                                        print(f"    ¡MOVIMIENTOS ENCONTRADOS! {len(movs)}")
                                        return movs
                                else:
                                    print(f"    Fuera del área bancaria, regresando...")
                                    scraper.driver.back()
                                    await asyncio.sleep(2)
                                    
                            except Exception as e:
                                print(f"    Error: {e}")
                                continue
                            
                            if enlaces_probados >= 10:  # Límite para no saturar
                                break
                    
                    if enlaces_probados >= 10:
                        break
                        
            except Exception as e:
                print(f"Error con texto '{text}': {e}")
                continue
        
        print(f"Total enlaces probados: {enlaces_probados}")
        return []
        
    except Exception as e:
        print(f"Error buscando enlaces de cuentas: {e}")
        return []

async def _probar_urls_bancarias(scraper):
    """Probar URLs específicas del área bancaria"""
    try:
        base_url = "https://bancaonline.bankinter.com"
        
        # URLs típicas de banca online de Bankinter
        urls_bancarias = [
            f"{base_url}/gestion/posicion",
            f"{base_url}/gestion/posicion.xhtml", 
            f"{base_url}/gestion/cuentas-corrientes",
            f"{base_url}/gestion/cuentas-corrientes.xhtml",
            f"{base_url}/gestion/movimientos",
            f"{base_url}/gestion/movimientos.xhtml",
            f"{base_url}/gestion/extractos", 
            f"{base_url}/gestion/extractos.xhtml",
            f"{base_url}/gestion/consultas",
            f"{base_url}/gestion/consultas.xhtml",
            f"{base_url}/gestion/operaciones",
            f"{base_url}/gestion/operaciones.xhtml",
            f"{base_url}/posicion-global",
            f"{base_url}/mis-cuentas",
            f"{base_url}/cuenta-corriente/movimientos"
        ]
        
        for url in urls_bancarias:
            try:
                print(f"  Probando: {url}")
                scraper.driver.get(url)
                await asyncio.sleep(3)
                
                final_url = scraper.driver.current_url
                print(f"    Resultado: {final_url}")
                
                # Verificar si es una página válida (no error 404)
                page_title = scraper.driver.title.lower()
                page_source = scraper.driver.page_source.lower()
                
                is_error = any(error in page_title for error in ['error', '404', 'not found']) or \
                          any(error in page_source for error in ['error 404', 'page not found', 'no encontrada'])
                
                if not is_error and "bancaonline.bankinter.com" in final_url:
                    print(f"    ✓ Página válida")
                    
                    # Tomar screenshot
                    scraper.driver.save_screenshot(f"banking_page_{int(time.time())}.png")
                    
                    # Buscar movimientos
                    movs = scraper._extract_transactions_from_current_page()
                    if movs:
                        print(f"    ¡MOVIMIENTOS! {len(movs)} encontrados")
                        return movs
                    
                    # Buscar formularios de consulta de movimientos
                    forms = scraper.driver.find_elements(By.TAG_NAME, "form")
                    date_inputs = scraper.driver.find_elements(By.CSS_SELECTOR, "input[type='date'], input[name*='fecha']")
                    
                    if forms and date_inputs:
                        print(f"    Formulario de consulta encontrado ({len(forms)} forms, {len(date_inputs)} date inputs)")
                        
                        # Intentar completar formulario con fechas
                        movs = await _completar_formulario_fechas(scraper, date_inputs)
                        if movs:
                            return movs
                
                else:
                    print(f"    ✗ Página inválida o error")
            
            except Exception as e:
                print(f"    Error: {e}")
                continue
        
        return []
        
    except Exception as e:
        print(f"Error probando URLs bancarias: {e}")
        return []

async def _explorar_frames(scraper):
    """Explorar frames e iframes que puedan contener datos bancarios"""
    try:
        # Buscar todos los frames
        frames = scraper.driver.find_elements(By.TAG_NAME, "iframe")
        frames.extend(scraper.driver.find_elements(By.TAG_NAME, "frame"))
        
        print(f"Frames encontrados: {len(frames)}")
        
        for i, frame in enumerate(frames):
            try:
                print(f"  Explorando frame {i+1}")
                
                # Cambiar al frame
                scraper.driver.switch_to.frame(frame)
                await asyncio.sleep(2)
                
                # Buscar movimientos en el frame
                movs = scraper._extract_transactions_from_current_page()
                if movs:
                    print(f"    ¡MOVIMIENTOS EN FRAME! {len(movs)}")
                    scraper.driver.switch_to.default_content()
                    return movs
                
                # Buscar formularios en el frame
                forms = scraper.driver.find_elements(By.TAG_NAME, "form")
                if forms:
                    print(f"    Formularios en frame: {len(forms)}")
                
                # Regresar al contenido principal
                scraper.driver.switch_to.default_content()
                
            except Exception as e:
                print(f"    Error con frame {i+1}: {e}")
                # Asegurar regreso al contenido principal
                try:
                    scraper.driver.switch_to.default_content()
                except:
                    pass
                continue
        
        return []
        
    except Exception as e:
        print(f"Error explorando frames: {e}")
        return []

async def _completar_formulario_fechas(scraper, date_inputs):
    """Intentar completar formulario con fechas para consultar movimientos"""
    try:
        if not date_inputs:
            return []
        
        print(f"    Intentando completar formulario de fechas...")
        
        # Fechas para consulta (agosto 2025)
        fecha_inicio = "01/08/2025"
        fecha_fin = "31/08/2025"
        
        # Completar campos de fecha
        for i, date_input in enumerate(date_inputs[:2]):  # Máximo 2 campos
            try:
                if i == 0:
                    date_input.clear()
                    date_input.send_keys(fecha_inicio)
                    print(f"      Fecha inicio: {fecha_inicio}")
                elif i == 1:
                    date_input.clear()
                    date_input.send_keys(fecha_fin)
                    print(f"      Fecha fin: {fecha_fin}")
            except Exception as e:
                print(f"      Error completando fecha {i+1}: {e}")
        
        # Buscar botón de consulta
        submit_selectors = [
            "input[type='submit']",
            "button[type='submit']", 
            "//button[contains(text(), 'consultar')]",
            "//button[contains(text(), 'buscar')]",
            "//input[@value='Consultar']",
            "//input[@value='Buscar']"
        ]
        
        for selector in submit_selectors:
            try:
                if selector.startswith("//"):
                    buttons = scraper.driver.find_elements(By.XPATH, selector)
                else:
                    buttons = scraper.driver.find_elements(By.CSS_SELECTOR, selector)
                
                if buttons:
                    button = buttons[0]
                    if button.is_displayed() and button.is_enabled():
                        print(f"      Haciendo clic en: {selector}")
                        button.click()
                        await asyncio.sleep(5)
                        
                        # Buscar resultados
                        movs = scraper._extract_transactions_from_current_page()
                        if movs:
                            print(f"      ¡RESULTADOS! {len(movs)} movimientos")
                            return movs
                        
                        break
                        
            except Exception as e:
                print(f"      Error con botón {selector}: {e}")
                continue
        
        return []
        
    except Exception as e:
        print(f"Error completando formulario: {e}")
        return []

async def _generar_mapa_navegacion(scraper):
    """Generar mapa de toda la navegación realizada"""
    try:
        current_url = scraper.driver.current_url
        page_title = scraper.driver.title
        
        print(f"=== MAPA DE NAVEGACION FINAL ===")
        print(f"URL actual: {current_url}")
        print(f"Título: {page_title}")
        
        # Contar elementos importantes
        links = len(scraper.driver.find_elements(By.TAG_NAME, "a"))
        forms = len(scraper.driver.find_elements(By.TAG_NAME, "form"))
        buttons = len(scraper.driver.find_elements(By.TAG_NAME, "button"))
        inputs = len(scraper.driver.find_elements(By.TAG_NAME, "input"))
        
        print(f"Elementos en página:")
        print(f"  Enlaces: {links}")
        print(f"  Formularios: {forms}")  
        print(f"  Botones: {buttons}")
        print(f"  Inputs: {inputs}")
        
        # Buscar palabras clave bancarias en la página
        page_text = scraper.driver.page_source.lower()
        banking_keywords = {
            'cuenta': page_text.count('cuenta'),
            'saldo': page_text.count('saldo'),
            'movimiento': page_text.count('movimiento'),
            'extracto': page_text.count('extracto'),
            'operacion': page_text.count('operacion'),
            'transferencia': page_text.count('transferencia')
        }
        
        print(f"Palabras clave bancarias:")
        for word, count in banking_keywords.items():
            if count > 0:
                print(f"  '{word}': {count} veces")
        
        # Screenshot final
        scraper.driver.save_screenshot("exploration_final_map.png")
        print(f"Screenshot final guardado: exploration_final_map.png")
        
    except Exception as e:
        print(f"Error generando mapa: {e}")

if __name__ == "__main__":
    try:
        resultado = asyncio.run(explore_real_banking())
        
        if resultado:
            print(f"\n" + "="*60)
            print(f"[EXITO] MOVIMIENTOS REALES ENCONTRADOS")
            print(f"="*60)
        else:
            print(f"\n" + "="*60)
            print(f"[INFO] EXPLORACION COMPLETA DEL AREA BANCARIA")
            print(f"Login exitoso pero movimientos no localizados")
            print(f"Posibles causas:")
            print(f"- Cuenta sin movimientos en agosto 2025")
            print(f"- Movimientos en sección requiere pasos adicionales")
            print(f"- Bankinter requiere autenticación adicional")
            print(f"="*60)
            
    except KeyboardInterrupt:
        print(f"\n[CANCELADO] Exploración interrumpida por usuario")
    except Exception as e:
        print(f"\n[ERROR] Error fatal: {e}")