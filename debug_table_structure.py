#!/usr/bin/env python3
"""
Debug para analizar la estructura exacta de la tabla de Bankinter
"""

import asyncio
import logging
from app.services.bankinter_scraper_v6 import BankinterScraperV6
from selenium.webdriver.common.by import By

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def debug_table_structure():
    """Analizar estructura exacta de la tabla"""
    
    username = "75867185"
    password = "Motoreta123$"
    
    print("DEBUG - ESTRUCTURA DE TABLA BANKINTER")
    print("=" * 60)
    
    scraper = None
    try:
        scraper = BankinterScraperV6(username=username, password=password)
        
        print("Configurando navegador...")
        scraper.setup_driver()
        
        print("Realizando login...")
        if not await scraper.login():
            print("ERROR: Login fallido")
            return
        
        print("Navegando a movimientos...")
        if not await scraper.navigate_to_movements():
            print("ERROR: Navegación fallida")
            return
        
        print("ANALIZANDO ESTRUCTURA DE TABLA...")
        
        # Encontrar tabla
        tables = scraper.driver.find_elements(By.TAG_NAME, "table")
        print(f"Tablas encontradas: {len(tables)}")
        
        for i, table in enumerate(tables):
            table_text = table.text.lower()
            if 'fecha' in table_text or 'importe' in table_text:
                print(f"\n=== TABLA {i+1} ===")
                
                rows = table.find_elements(By.TAG_NAME, "tr")
                print(f"Filas total: {len(rows)}")
                
                # Analizar primeras 5 filas para entender estructura
                for j, row in enumerate(rows[:5]):
                    print(f"\n--- FILA {j+1} ---")
                    
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if not cells:
                        cells = row.find_elements(By.TAG_NAME, "th")  # Headers
                    
                    print(f"Celdas en fila: {len(cells)}")
                    
                    for k, cell in enumerate(cells):
                        text = cell.text.strip()
                        print(f"  Celda {k+1}: '{text[:100]}'")
                        
                        # Verificar si contiene fecha
                        if any(month in text.lower() for month in ['agosto', '/08/', '2025']):
                            print(f"    -> CONTIENE FECHA")
                        
                        # Verificar si contiene importe
                        if '€' in text or any(char in text for char in ['+', '-']) and any(char.isdigit() for char in text):
                            print(f"    -> POSIBLE IMPORTE")
                        
                        # Verificar si contiene saldo
                        if 'saldo' in text.lower():
                            print(f"    -> POSIBLE SALDO")
                
                # Analizar algunas filas de agosto específicamente
                print(f"\n=== FILAS DE AGOSTO 2025 ===")
                august_rows_found = 0
                
                for j, row in enumerate(rows):
                    if august_rows_found >= 3:  # Solo primeras 3 filas de agosto
                        break
                        
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) == 0:
                        continue
                    
                    row_text = " ".join([cell.text.strip() for cell in cells])
                    
                    # Verificar si es fila de agosto 2025
                    if ('08/2025' in row_text or 'agosto' in row_text.lower()) and '2025' in row_text:
                        august_rows_found += 1
                        print(f"\n--- FILA AGOSTO {august_rows_found} (Fila {j+1}) ---")
                        print(f"Texto completo: {row_text}")
                        
                        print(f"Celdas individuales:")
                        for k, cell in enumerate(cells):
                            text = cell.text.strip()
                            print(f"  [{k+1}] '{text}'")
                            
                            # Analizar contenido de cada celda
                            if any(date_indicator in text for date_indicator in ['/08/', '2025', 'agosto']):
                                print(f"      -> FECHA detectada")
                            
                            if '€' in text and any(char.isdigit() for char in text):
                                print(f"      -> IMPORTE/SALDO con €: {text}")
                                
                                # Intentar extraer números
                                import re
                                numbers = re.findall(r'[+-]?\d+[\s,\.]*\d*', text)
                                print(f"      -> Números encontrados: {numbers}")
                            
                            if len(text) > 20 and not ('€' in text) and not any(date_indicator in text for date_indicator in ['/08/', '2025']):
                                print(f"      -> Posible CONCEPTO")
                
                break  # Solo analizar primera tabla válida
        
        # Guardar HTML para análisis manual
        page_source = scraper.driver.page_source
        with open("debug_bankinter_table.html", "w", encoding="utf-8", errors="ignore") as f:
            f.write(page_source)
        print(f"\nHTML completo guardado en: debug_bankinter_table.html")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    asyncio.run(debug_table_structure())