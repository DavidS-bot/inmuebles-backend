#!/usr/bin/env python3
"""
Mostrar los datos raw de la página de movimientos
"""

import asyncio
import re
from datetime import date
from app.services.bankinter_scraper_v2 import BankinterScraperV2
from selenium.webdriver.common.by import By

async def show_raw_data():
    """Mostrar datos raw sin procesamiento"""
    
    username = "75867185"
    password = "Motoreta123$"
    
    print("MOSTRANDO DATOS RAW DE LA PAGINA")
    print("=" * 60)
    
    scraper = None
    try:
        scraper = BankinterScraperV2(username=username, password=password)
        scraper.setup_driver()
        
        print("Login...")
        if not await scraper.login():
            return
        
        print("Navegando a area bancaria...")
        scraper.driver.get("https://bancaonline.bankinter.com/gestion/posicion.xhtml")
        await asyncio.sleep(5)
        
        current_url = scraper.driver.current_url
        print(f"URL actual: {current_url}")
        
        # Obtener el HTML completo
        page_source = scraper.driver.page_source
        
        print(f"\n=== ANALISIS DE DATOS RAW ===")
        print(f"Tamaño página: {len(page_source):,} caracteres")
        
        # 1. Buscar todas las referencias a agosto 2025
        print(f"\n1. FECHAS DE AGOSTO 2025:")
        agosto_patterns = [
            r'08[/-]2025',
            r'2025[/-]08', 
            r'2025-08-\d{2}',
            r'\d{2}[/-]08[/-]2025',
            r'agosto.*2025',
            r'aug.*2025'
        ]
        
        all_agosto_matches = []
        for pattern in agosto_patterns:
            matches = re.findall(pattern, page_source, re.IGNORECASE)
            all_agosto_matches.extend(matches)
        
        unique_agosto = list(set(all_agosto_matches))
        print(f"Fechas agosto encontradas: {len(unique_agosto)}")
        for i, fecha in enumerate(unique_agosto[:10], 1):
            print(f"  {i}. {fecha}")
        
        # 2. Buscar patrones de dinero cerca de fechas de agosto
        print(f"\n2. LINEAS CON FECHAS DE AGOSTO Y NUMEROS:")
        lines = page_source.split('\n')
        agosto_money_lines = []
        
        for i, line in enumerate(lines):
            line_clean = line.strip()
            if line_clean and any(re.search(pattern, line_clean, re.IGNORECASE) for pattern in agosto_patterns):
                # Buscar números que parezcan dinero en líneas cercanas
                context_lines = lines[max(0, i-2):min(len(lines), i+3)]
                context_text = ' '.join([l.strip() for l in context_lines if l.strip()])
                
                # Buscar patrones de dinero
                money_matches = re.findall(r'\d+[.,]\d{2}(?:\s*€|EUR)?', context_text)
                if money_matches:
                    agosto_money_lines.append({
                        'line': line_clean[:100],
                        'context': context_text[:200],
                        'money': money_matches
                    })
        
        print(f"Líneas con fechas de agosto + dinero: {len(agosto_money_lines)}")
        for i, item in enumerate(agosto_money_lines[:5], 1):
            print(f"  {i}. Línea: {item['line']}")
            print(f"     Dinero: {item['money']}")
            print(f"     Contexto: {item['context'][:100]}...")
            print()
        
        # 3. Buscar estructuras HTML específicas
        print(f"\n3. ELEMENTOS HTML CON DATOS BANCARIOS:")
        
        # Buscar todos los divs con clases que puedan contener movimientos
        potential_divs = scraper.driver.find_elements(By.CSS_SELECTOR, 
            "div[class*='movement'], div[class*='transaction'], div[class*='row'], div[class*='item'], div[class*='entry']")
        
        print(f"Divs potenciales: {len(potential_divs)}")
        
        # Buscar elementos que contengan fechas de agosto
        agosto_elements = []
        all_elements = scraper.driver.find_elements(By.XPATH, "//*[contains(text(), '08') and contains(text(), '2025')]")
        
        print(f"Elementos con '08' y '2025': {len(all_elements)}")
        
        for i, element in enumerate(all_elements[:10]):
            try:
                text = element.text.strip()
                tag = element.tag_name
                classes = element.get_attribute('class') or ''
                
                if text and ('08' in text or 'agosto' in text.lower()) and '2025' in text:
                    agosto_elements.append({
                        'tag': tag,
                        'class': classes,
                        'text': text[:100],
                        'html': element.get_attribute('outerHTML')[:200]
                    })
            except:
                continue
        
        print(f"Elementos específicos de agosto 2025: {len(agosto_elements)}")
        for i, elem in enumerate(agosto_elements[:5], 1):
            print(f"  {i}. Tag: {elem['tag']}, Clase: '{elem['class'][:30]}'")
            print(f"     Texto: {elem['text']}")
            print(f"     HTML: {elem['html']}")
            print()
        
        # 4. Buscar tablas con datos
        print(f"\n4. TABLAS CON DATOS:")
        tables = scraper.driver.find_elements(By.TAG_NAME, "table")
        print(f"Tablas encontradas: {len(tables)}")
        
        for i, table in enumerate(tables[:3]):
            try:
                rows = table.find_elements(By.TAG_NAME, "tr")
                print(f"  Tabla {i+1}: {len(rows)} filas")
                
                # Mostrar contenido si tiene agosto
                table_html = table.get_attribute('outerHTML')
                if '08' in table_html and '2025' in table_html:
                    print(f"    ¡CONTIENE DATOS DE AGOSTO 2025!")
                    
                    # Mostrar primeras filas
                    for j, row in enumerate(rows[:5]):
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if cells:
                            row_data = [cell.text.strip() for cell in cells]
                            if any('08' in cell or '2025' in cell for cell in row_data):
                                print(f"      Fila {j+1}: {' | '.join(row_data[:5])}")
                        
            except Exception as e:
                print(f"    Error: {e}")
        
        # 5. Texto raw con patrones específicos
        print(f"\n5. BUSQUEDA DE PATRONES ESPECIFICOS:")
        
        # Patrón típico: fecha - descripción - importe
        movement_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]2025).*?(\d+[.,]\d{2})'
        movements = re.findall(movement_pattern, page_source)
        
        agosto_movements = [m for m in movements if '08' in m[0] or '/8/' in m[0]]
        
        print(f"Movimientos de agosto encontrados: {len(agosto_movements)}")
        for i, (fecha, importe) in enumerate(agosto_movements[:10], 1):
            print(f"  {i}. {fecha} - {importe}")
        
        # 6. JavaScript para extraer datos dinámicos
        print(f"\n6. EXTRACCION CON JAVASCRIPT:")
        try:
            js_result = scraper.driver.execute_script("""
                // Buscar todos los elementos con texto que contenga fechas de agosto
                var elements = document.querySelectorAll('*');
                var results = [];
                
                for (var i = 0; i < elements.length; i++) {
                    var el = elements[i];
                    var text = el.textContent || el.innerText || '';
                    
                    if (text.includes('08') && text.includes('2025')) {
                        results.push({
                            tag: el.tagName,
                            class: el.className,
                            text: text.trim().substring(0, 100),
                            style: el.style.cssText
                        });
                    }
                }
                
                return results.slice(0, 10); // Solo primeros 10
            """)
            
            print(f"Elementos con JavaScript: {len(js_result)}")
            for i, elem in enumerate(js_result[:5], 1):
                print(f"  {i}. {elem['tag']} - {elem['text'][:50]}")
                
        except Exception as e:
            print(f"Error con JavaScript: {e}")
        
        # Guardar HTML completo para análisis manual
        with open("bankinter_page_raw.html", "w", encoding="utf-8") as f:
            f.write(page_source)
        print(f"\n📄 HTML completo guardado en: bankinter_page_raw.html")
        
        # Tomar screenshot final
        scraper.driver.save_screenshot("bankinter_raw_data.png")
        print(f"📷 Screenshot guardado en: bankinter_raw_data.png")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False
        
    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    asyncio.run(show_raw_data())