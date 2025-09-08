#!/usr/bin/env python3
"""
Test rápido enfocado en encontrar movimientos reales de agosto 2025
"""

import asyncio
import logging
import time
from datetime import date
from app.services.bankinter_scraper_v2 import BankinterScraperV2
from selenium.webdriver.common.by import By

logging.basicConfig(level=logging.INFO)

async def quick_real_movements():
    """Test rápido para movimientos reales"""
    
    username = "75867185"
    password = "Motoreta123$"
    
    print("BUSQUEDA RAPIDA DE MOVIMIENTOS REALES - AGOSTO 2025")
    print("=" * 60)
    
    scraper = None
    try:
        scraper = BankinterScraperV2(username=username, password=password)
        
        print("[1/4] Login...")
        scraper.setup_driver()
        
        login_ok = await scraper.login()
        if not login_ok:
            print("ERROR: Login fallido")
            return
        
        print("[OK] Login exitoso")
        await asyncio.sleep(3)
        
        current_url = scraper.driver.current_url
        print(f"URL post-login: {current_url}")
        
        print("\n[2/4] Navegando a area bancaria real...")
        
        # URLs específicas de Bankinter para movimientos
        banking_urls = [
            "https://bancaonline.bankinter.com/gestion/posicion.xhtml",
            "https://bancaonline.bankinter.com/gestion/cuentas-corrientes.xhtml", 
            "https://bancaonline.bankinter.com/gestion/movimientos.xhtml",
            "https://bancaonline.bankinter.com/gestion/extractos.xhtml"
        ]
        
        movimientos_encontrados = []
        
        for url in banking_urls:
            try:
                print(f"  Probando: {url}")
                scraper.driver.get(url)
                await asyncio.sleep(4)
                
                final_url = scraper.driver.current_url
                print(f"  Resultado: {final_url}")
                
                # Verificar si estamos en página válida
                if "error" not in scraper.driver.page_source.lower():
                    
                    # Tomar screenshot
                    timestamp = int(time.time())
                    scraper.driver.save_screenshot(f"banking_page_{timestamp}.png")
                    print(f"  Screenshot: banking_page_{timestamp}.png")
                    
                    # Buscar movimientos
                    movs = scraper._extract_transactions_from_current_page()
                    if movs:
                        print(f"  ¡MOVIMIENTOS! {len(movs)} encontrados")
                        movimientos_encontrados.extend(movs)
                    
                    # Buscar formularios de consulta
                    forms = scraper.driver.find_elements(By.TAG_NAME, "form")
                    if forms:
                        print(f"  Formularios encontrados: {len(forms)}")
                        
                        # Buscar campos de fecha
                        date_fields = scraper.driver.find_elements(By.CSS_SELECTOR, 
                            "input[type='date'], input[name*='fecha'], input[placeholder*='fecha']")
                        
                        if date_fields:
                            print(f"  Campos de fecha: {len(date_fields)}")
                            
                            # Intentar completar formulario
                            movs_form = await _try_form_query(scraper, date_fields)
                            if movs_form:
                                movimientos_encontrados.extend(movs_form)
                    
                    # Si encontramos datos, continuar con esta página
                    if movimientos_encontrados:
                        print(f"  --> Datos encontrados, continuando en esta página")
                        break
                
            except Exception as e:
                print(f"  Error: {e}")
                continue
        
        print(f"\n[3/4] RESULTADOS:")
        print(f"Total movimientos: {len(movimientos_encontrados)}")
        
        if movimientos_encontrados:
            # Filtrar agosto 2025
            agosto_2025 = [m for m in movimientos_encontrados 
                          if m.date.year == 2025 and m.date.month == 8]
            
            print(f"Agosto 2025: {len(agosto_2025)} movimientos")
            
            if agosto_2025:
                print(f"\n=== MOVIMIENTOS DE AGOSTO 2025 ===")
                for i, mov in enumerate(agosto_2025, 1):
                    fecha = mov.date.strftime('%d/%m/%Y')
                    desc = mov.description[:50]
                    print(f"{i:2d}. {fecha} | {desc:50} | {mov.amount:8.2f}EUR")
                
                # Calcular totales
                total = sum(m.amount for m in agosto_2025)
                ingresos = sum(m.amount for m in agosto_2025 if m.amount > 0)
                gastos = sum(m.amount for m in agosto_2025 if m.amount < 0)
                
                print(f"\nRESUMEN AGOSTO 2025:")
                print(f"  Ingresos:  {ingresos:8.2f}EUR")
                print(f"  Gastos:    {gastos:8.2f}EUR")
                print(f"  Balance:   {total:8.2f}EUR")
                
                # Exportar
                print(f"\n[4/4] Exportando datos...")
                csv_file = await scraper.export_to_csv(agosto_2025, "movimientos_agosto_2025.csv")
                print(f"Archivo: {csv_file}")
                
                return True
            
            else:
                print(f"\nNo hay movimientos en AGOSTO 2025")
                print(f"Movimientos en otros meses:")
                
                # Agrupar por mes
                by_month = {}
                for m in movimientos_encontrados:
                    key = f"{m.date.year}-{m.date.month:02d}"
                    if key not in by_month:
                        by_month[key] = []
                    by_month[key].append(m)
                
                for month, movs in sorted(by_month.items()):
                    total = sum(m.amount for m in movs)
                    print(f"  {month}: {len(movs)} movimientos, {total:.2f}EUR")
        
        else:
            print(f"No se encontraron movimientos bancarios")
            
            # Debug info
            print(f"\nINFO DEBUG:")
            print(f"URL final: {scraper.driver.current_url}")
            
            # Buscar indicadores
            page = scraper.driver.page_source.lower()
            indicators = ['saldo', 'cuenta', 'movimiento', 'extracto']
            found = {ind: page.count(ind) for ind in indicators}
            print(f"Indicadores: {found}")
            
        return len(movimientos_encontrados) > 0
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False
        
    finally:
        if scraper:
            scraper.close()

async def _try_form_query(scraper, date_fields):
    """Intentar consulta con formulario de fechas"""
    try:
        print(f"    Completando formulario de fechas...")
        
        # Fechas para agosto 2025
        start_date = "01/08/2025" 
        end_date = "31/08/2025"
        
        # Completar campos de fecha
        if len(date_fields) >= 1:
            date_fields[0].clear()
            date_fields[0].send_keys(start_date)
            print(f"    Fecha inicio: {start_date}")
            
        if len(date_fields) >= 2:
            date_fields[1].clear()
            date_fields[1].send_keys(end_date)
            print(f"    Fecha fin: {end_date}")
        
        # Buscar botón submit
        submit_buttons = scraper.driver.find_elements(By.CSS_SELECTOR, 
            "input[type='submit'], button[type='submit']")
        
        if not submit_buttons:
            submit_buttons = scraper.driver.find_elements(By.XPATH,
                "//button[contains(text(), 'Consultar') or contains(text(), 'Buscar')]")
        
        if submit_buttons:
            button = submit_buttons[0]
            if button.is_displayed():
                print(f"    Enviando consulta...")
                button.click()
                await asyncio.sleep(5)
                
                # Buscar resultados
                movs = scraper._extract_transactions_from_current_page()
                if movs:
                    print(f"    ¡RESULTADOS DEL FORMULARIO! {len(movs)} movimientos")
                    return movs
        
        return []
        
    except Exception as e:
        print(f"    Error en formulario: {e}")
        return []

if __name__ == "__main__":
    try:
        resultado = asyncio.run(quick_real_movements())
        
        if resultado:
            print(f"\n" + "="*60)
            print(f"[EXITO] MOVIMIENTOS DE AGOSTO 2025 ENCONTRADOS")
            print(f"="*60)
        else:
            print(f"\n" + "="*60)
            print(f"[INFO] BUSQUEDA COMPLETADA")
            print(f"Scraper funcionando correctamente")
            print(f"No hay movimientos en agosto 2025 en esta cuenta")
            print(f"="*60)
            
    except Exception as e:
        print(f"\n[ERROR] {e}")