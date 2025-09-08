#!/usr/bin/env python3
"""
Test accediendo directamente a la URL correcta de movimientos
"""

import asyncio
import logging
from datetime import date
from app.services.bankinter_scraper_v2 import BankinterScraperV2
from selenium.webdriver.common.by import By

logging.basicConfig(level=logging.INFO)

async def test_correct_url():
    """Test con la URL correcta de movimientos"""
    
    username = "75867185"
    password = "Motoreta123$"
    
    # URL correcta proporcionada por el usuario
    MOVIMIENTOS_URL = "https://bancaonline.bankinter.com/extracto/secure/movimientos_cuenta.xhtml?INDEX_CTA=1&IND=C&TIPO=N"
    
    print("TEST CON URL CORRECTA DE MOVIMIENTOS")
    print("=" * 60)
    print(f"URL objetivo: {MOVIMIENTOS_URL}")
    
    scraper = None
    try:
        scraper = BankinterScraperV2(username=username, password=password)
        
        print("\n[1/4] Realizando login...")
        scraper.setup_driver()
        
        login_ok = await scraper.login()
        if not login_ok:
            print("ERROR: Login fallido")
            return
        
        print("OK - Login exitoso")
        await asyncio.sleep(3)
        
        print(f"\n[2/4] Navegando a URL correcta de movimientos...")
        print(f"Accediendo a: {MOVIMIENTOS_URL}")
        
        # Navegar directamente a la URL correcta
        scraper.driver.get(MOVIMIENTOS_URL)
        await asyncio.sleep(5)
        
        current_url = scraper.driver.current_url
        print(f"URL actual: {current_url}")
        
        # Tomar screenshot de la página de movimientos
        scraper.driver.save_screenshot("movimientos_page_correct.png")
        print("Screenshot guardado: movimientos_page_correct.png")
        
        print(f"\n[3/4] Analizando contenido de la página...")
        
        # Verificar si llegamos a la página correcta
        page_source = scraper.driver.page_source
        page_title = scraper.driver.title
        
        print(f"Título de página: {page_title}")
        print(f"Tamaño contenido: {len(page_source)} caracteres")
        
        # Buscar indicadores de que estamos en movimientos
        movement_indicators = [
            'movimiento', 'extracto', 'saldo', 'fecha', 'importe', 
            'concepto', 'cargo', 'abono', 'operacion'
        ]
        
        found_indicators = []
        for indicator in movement_indicators:
            count = page_source.lower().count(indicator)
            if count > 0:
                found_indicators.append(f"{indicator}({count})")
        
        print(f"Indicadores encontrados: {', '.join(found_indicators)}")
        
        # Buscar tablas que puedan contener movimientos
        tables = scraper.driver.find_elements(By.TAG_NAME, "table")
        print(f"Tablas encontradas: {len(tables)}")
        
        # Buscar formularios de consulta de fechas
        forms = scraper.driver.find_elements(By.TAG_NAME, "form")
        date_inputs = scraper.driver.find_elements(By.CSS_SELECTOR, 
            "input[type='date'], input[name*='fecha'], input[placeholder*='fecha']")
        
        print(f"Formularios: {len(forms)}, Campos de fecha: {len(date_inputs)}")
        
        print(f"\n[4/4] Extrayendo movimientos...")
        
        # Intentar extraer movimientos con el método actual
        movimientos = scraper._extract_transactions_from_current_page()
        
        if movimientos:
            print(f"EXITO: {len(movimientos)} movimientos encontrados")
            
            # Filtrar agosto 2025
            agosto_2025 = [m for m in movimientos if m.date.year == 2025 and m.date.month == 8]
            
            print(f"Movimientos de agosto 2025: {len(agosto_2025)}")
            
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
                print(f"  Total movimientos: {len(agosto_2025)}")
                print(f"  Ingresos: {ingresos:8.2f}EUR")
                print(f"  Gastos: {gastos:8.2f}EUR")
                print(f"  Balance: {total:8.2f}EUR")
                
                # Exportar
                csv_file = await scraper.export_to_csv(agosto_2025, "movimientos_agosto_2025_real.csv")
                print(f"\nExportado a: {csv_file}")
                
                return True
            
            else:
                print("No hay movimientos específicamente de agosto 2025")
                
                # Mostrar todos los movimientos encontrados
                print(f"\n=== TODOS LOS MOVIMIENTOS ENCONTRADOS ===")
                by_month = {}
                for m in movimientos:
                    key = f"{m.date.year}-{m.date.month:02d}"
                    if key not in by_month:
                        by_month[key] = []
                    by_month[key].append(m)
                
                for month, movs in sorted(by_month.items()):
                    total = sum(m.amount for m in movs)
                    print(f"  {month}: {len(movs)} movimientos, {total:.2f}EUR")
        
        else:
            print("No se encontraron movimientos con el método actual")
            
            # Análisis manual de la página
            print(f"\nANALISIS MANUAL DE LA PAGINA:")
            
            # Buscar texto que contenga fechas de agosto 2025
            import re
            
            # Buscar patrones de fecha
            date_patterns = re.findall(r'\d{1,2}[/-]\d{1,2}[/-]2025', page_source)
            agosto_dates = [d for d in date_patterns if '/08/' in d or '/8/' in d]
            
            print(f"Fechas de agosto encontradas: {len(agosto_dates)}")
            if agosto_dates:
                print(f"  Ejemplos: {agosto_dates[:5]}")
            
            # Buscar patrones de dinero cerca de fechas de agosto
            lines = page_source.split('\n')
            agosto_lines = []
            
            for line in lines:
                if ('08/2025' in line or '/08/' in line or '/8/' in line) and '2025' in line:
                    # Buscar números que parezcan importes
                    money_pattern = re.findall(r'\d+[.,]\d{2}', line)
                    if money_pattern:
                        agosto_lines.append(line.strip()[:100])
            
            print(f"Líneas con fechas de agosto y importes: {len(agosto_lines)}")
            for i, line in enumerate(agosto_lines[:3]):
                print(f"  {i+1}. {line}")
            
            # Si hay datos pero no se extrajeron, el problema está en el parser
            if agosto_lines:
                print(f"\nPROBLEMA: Hay datos de agosto pero el parser no los extrae")
                print(f"Necesitamos mejorar el método _extract_transactions_from_current_page")
            
        return len(movimientos) > 0
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False
        
    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    try:
        resultado = asyncio.run(test_correct_url())
        
        if resultado:
            print(f"\n" + "="*60)
            print(f"EXITO: ACCESO A PAGINA CORRECTA DE MOVIMIENTOS")
            print(f"="*60)
        else:
            print(f"\n" + "="*60)
            print(f"INFO: ACCESO EXITOSO PERO SIN EXTRAER DATOS")
            print(f"El parser necesita ajustes para esta página específica")
            print(f"="*60)
            
    except Exception as e:
        print(f"\nERROR: {e}")