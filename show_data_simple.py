#!/usr/bin/env python3
"""
Mostrar datos simple sin emojis
"""

import asyncio
import re
from app.services.bankinter_scraper_v2 import BankinterScraperV2
from selenium.webdriver.common.by import By

async def show_simple_data():
    """Mostrar datos de manera simple"""
    
    username = "75867185"
    password = "Motoreta123$"
    
    print("MOSTRANDO DATOS DE LA PAGINA DE MOVIMIENTOS")
    print("=" * 60)
    
    scraper = None
    try:
        scraper = BankinterScraperV2(username=username, password=password)
        scraper.setup_driver()
        
        print("1. Realizando login...")
        if not await scraper.login():
            print("Login fallido")
            return
        
        print("2. Navegando...")
        
        # Probar diferentes URLs para encontrar los datos
        urls_to_try = [
            "https://bancaonline.bankinter.com/gestion/posicion.xhtml",
            "https://bancaonline.bankinter.com/gestion/cuentas.xhtml",
            "https://bancaonline.bankinter.com/gestion/movimientos.xhtml"
        ]
        
        data_found = False
        
        for url in urls_to_try:
            print(f"   Probando: {url}")
            scraper.driver.get(url)
            await asyncio.sleep(4)
            
            current_url = scraper.driver.current_url
            page_source = scraper.driver.page_source
            page_size = len(page_source)
            
            print(f"   URL final: {current_url}")
            print(f"   Tamaño: {page_size} caracteres")
            
            if page_size > 1000:  # Si la página tiene contenido real
                print(f"   -> Contenido encontrado")
                
                # Buscar referencias a agosto
                agosto_count = page_source.lower().count('agosto')
                aug_count = page_source.count('08')
                year_count = page_source.count('2025')
                
                print(f"   Referencias: 'agosto'={agosto_count}, '08'={aug_count}, '2025'={year_count}")
                
                if aug_count > 0 and year_count > 0:
                    print(f"   *** DATOS DE AGOSTO 2025 ENCONTRADOS ***")
                    data_found = True
                    break
        
        if not data_found:
            print("No se encontraron datos, intentando URL directa...")
            target_url = "https://bancaonline.bankinter.com/extracto/secure/movimientos_cuenta.xhtml?INDEX_CTA=1&IND=C&TIPO=N"
            scraper.driver.get(target_url)
            await asyncio.sleep(5)
            
            current_url = scraper.driver.current_url
            page_source = scraper.driver.page_source
            
            print(f"URL directa result: {current_url}")
            print(f"Tamaño: {len(page_source)} caracteres")
        
        print(f"\n3. ANALIZANDO CONTENIDO ACTUAL...")
        
        current_url = scraper.driver.current_url
        page_source = scraper.driver.page_source
        
        print(f"URL final: {current_url}")
        print(f"Titulo: {scraper.driver.title}")
        print(f"Tamaño página: {len(page_source)} caracteres")
        
        # Guardar HTML para análisis
        with open("page_content.html", "w", encoding="utf-8", errors="ignore") as f:
            f.write(page_source)
        print(f"HTML guardado en: page_content.html")
        
        # Screenshot
        scraper.driver.save_screenshot("page_screenshot.png")
        print(f"Screenshot: page_screenshot.png")
        
        # Buscar patrones básicos
        print(f"\n4. PATRONES ENCONTRADOS:")
        
        patterns = {
            'agosto': page_source.lower().count('agosto'),
            'aug': page_source.lower().count('aug'),
            '08': page_source.count('08'),
            '2025': page_source.count('2025'),
            'movimiento': page_source.lower().count('movimiento'),
            'saldo': page_source.lower().count('saldo'),
            'cuenta': page_source.lower().count('cuenta'),
            'euro': page_source.lower().count('euro'),
            'eur': page_source.lower().count('eur')
        }
        
        for pattern, count in patterns.items():
            print(f"   '{pattern}': {count} veces")
        
        # Buscar fechas específicas de agosto 2025
        agosto_patterns = [
            r'\d{1,2}[/-]08[/-]2025',
            r'08[/-]\d{1,2}[/-]2025', 
            r'2025[/-]08[/-]\d{1,2}',
            r'agosto.*2025'
        ]
        
        print(f"\n5. FECHAS DE AGOSTO 2025:")
        all_dates = []
        for pattern in agosto_patterns:
            matches = re.findall(pattern, page_source, re.IGNORECASE)
            all_dates.extend(matches)
        
        unique_dates = list(set(all_dates))
        print(f"Fechas únicas encontradas: {len(unique_dates)}")
        
        for i, date in enumerate(unique_dates[:10], 1):
            print(f"   {i}. {date}")
        
        # Buscar números que parezcan importes
        print(f"\n6. IMPORTES ENCONTRADOS:")
        money_patterns = [
            r'\d+[.,]\d{2}\s*€',
            r'\d+[.,]\d{2}\s*EUR',
            r'\d+[.,]\d{2}\s*euros?'
        ]
        
        all_money = []
        for pattern in money_patterns:
            matches = re.findall(pattern, page_source, re.IGNORECASE)
            all_money.extend(matches)
        
        unique_money = list(set(all_money))
        print(f"Importes encontrados: {len(unique_money)}")
        
        for i, money in enumerate(unique_money[:10], 1):
            print(f"   {i}. {money}")
        
        # Si hay fechas de agosto Y importes, buscar contexto
        if unique_dates and unique_money:
            print(f"\n7. CONTEXTO DE DATOS:")
            lines = page_source.split('\n')
            
            relevant_lines = []
            for line in lines:
                line_clean = line.strip()
                if (any(date_part in line_clean for date_part in ['08', 'agosto']) and 
                    '2025' in line_clean and 
                    any(money_indicator in line_clean for money_indicator in [',', '.', '€', 'EUR'])):
                    relevant_lines.append(line_clean[:100])
            
            print(f"Líneas relevantes: {len(relevant_lines)}")
            for i, line in enumerate(relevant_lines[:5], 1):
                print(f"   {i}. {line}")
        
        # Elementos HTML específicos
        print(f"\n8. ELEMENTOS HTML:")
        
        try:
            # Contar elementos básicos
            divs = len(scraper.driver.find_elements(By.TAG_NAME, "div"))
            tables = len(scraper.driver.find_elements(By.TAG_NAME, "table"))
            spans = len(scraper.driver.find_elements(By.TAG_NAME, "span"))
            
            print(f"   Divs: {divs}")
            print(f"   Tablas: {tables}") 
            print(f"   Spans: {spans}")
            
            # Buscar elementos que contengan '08' y '2025'
            elements_with_agosto = scraper.driver.find_elements(By.XPATH, 
                "//*[contains(text(), '08') and contains(text(), '2025')]")
            
            print(f"   Elementos con '08' y '2025': {len(elements_with_agosto)}")
            
            for i, elem in enumerate(elements_with_agosto[:5], 1):
                try:
                    text = elem.text.strip()[:50]
                    tag = elem.tag_name
                    print(f"      {i}. {tag}: {text}")
                except:
                    pass
                    
        except Exception as e:
            print(f"   Error analizando HTML: {e}")
        
        return True
        
    except Exception as e:
        print(f"ERROR GENERAL: {e}")
        return False
        
    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    asyncio.run(show_simple_data())