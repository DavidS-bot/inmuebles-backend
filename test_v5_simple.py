#!/usr/bin/env python3
"""
Test scraper v5 sin emojis para Windows
"""

import asyncio
import logging
from app.services.bankinter_scraper_v5 import BankinterScraperV5

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_v5_simple():
    """Test simple del scraper v5"""
    
    username = "75867185"
    password = "Motoreta123$"
    
    print("BANKINTER SCRAPER V5 - FLUJO EXACTO DE NAVEGACION")
    print("=" * 60)
    print(f"Usuario: {username}")
    print(f"Objetivo: movimientos_cuenta.xhtml o clic en ES0201280730910160000605")
    
    scraper = None
    try:
        scraper = BankinterScraperV5(username=username, password=password)
        
        print(f"\n[1/4] Configurando navegador...")
        scraper.setup_driver()
        print("OK - Navegador configurado")
        
        print(f"\n[2/4] Login...")
        login_success = await scraper.login()
        
        if not login_success:
            print("ERROR - Login fallido")
            return False
        
        print("OK - Login exitoso")
        
        print(f"\n[3/4] Navegando a movimientos...")
        navigation_success = await scraper.navigate_to_movements()
        
        if not navigation_success:
            print("ERROR - Navegacion fallida")
            current_url = scraper.driver.current_url
            print(f"URL actual: {current_url}")
            return False
        
        print("OK - Navegacion exitosa")
        
        print(f"\n[4/4] Extrayendo movimientos de agosto 2025...")
        august_transactions = await scraper.extract_real_movements()
        
        # Filtrar solo agosto 2025
        august_only = [t for t in august_transactions if t.date.year == 2025 and t.date.month == 8]
        
        print(f"\nRESULTADOS:")
        print(f"Total movimientos extraidos: {len(august_transactions)}")
        print(f"Movimientos agosto 2025: {len(august_only)}")
        
        if august_only:
            print(f"\nMOVIMIENTOS DE AGOSTO 2025:")
            print(f"{'Fecha':<12} {'Descripcion':<40} {'Importe':<12}")
            print("-" * 65)
            
            total = 0
            for i, t in enumerate(august_only, 1):
                fecha = t.date.strftime('%d/%m/%Y')
                desc = t.description[:37] + "..." if len(t.description) > 40 else t.description
                importe = f"{t.amount:+.2f}EUR"
                
                print(f"{fecha:<12} {desc:<40} {importe:<12}")
                total += t.amount
            
            print("-" * 65)
            print(f"TOTAL: {total:.2f}EUR")
            
            # Exportar
            csv_file = await scraper.export_to_csv(august_only, "agosto_2025_exacto.csv")
            print(f"\nExportado: {csv_file}")
            
            return True
            
        elif august_transactions:
            print(f"\nSin movimientos de agosto 2025, pero se encontraron otros:")
            
            # Agrupar por mes
            by_month = {}
            for t in august_transactions:
                key = f"{t.date.year}-{t.date.month:02d}"
                if key not in by_month:
                    by_month[key] = []
                by_month[key].append(t)
            
            for month, movs in sorted(by_month.items()):
                total_month = sum(m.amount for m in movs)
                print(f"  {month}: {len(movs)} movimientos, {total_month:.2f}EUR")
            
            # Exportar todo
            csv_file = await scraper.export_to_csv(august_transactions, "todos_movimientos_v5.csv")
            print(f"\nTodos exportados: {csv_file}")
            
            return True
        
        else:
            print("No se encontraron movimientos")
            
            # Debug
            current_url = scraper.driver.current_url
            page_source = scraper.driver.page_source
            
            print(f"\nDEBUG:")
            print(f"URL: {current_url}")
            print(f"Tamano pagina: {len(page_source):,} caracteres")
            
            # Contar palabras clave
            page_lower = page_source.lower()
            keywords = {
                'agosto': page_lower.count('agosto'),
                '08': page_lower.count('08'), 
                '2025': page_lower.count('2025'),
                'movimiento': page_lower.count('movimiento'),
                'euro': page_lower.count('euro')
            }
            
            print(f"Palabras clave:")
            for word, count in keywords.items():
                print(f"  {word}: {count}")
            
            # Guardar HTML
            with open("debug_v5.html", "w", encoding="utf-8", errors="ignore") as f:
                f.write(page_source)
            print(f"HTML guardado: debug_v5.html")
            
            return False
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False
        
    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    try:
        resultado = asyncio.run(test_v5_simple())
        
        if resultado:
            print(f"\n" + "="*60)
            print(f"EXITO: SCRAPER V5 FUNCIONA CON FLUJO EXACTO")
            print(f"="*60)
        else:
            print(f"\n" + "="*60)
            print(f"INFO: FLUJO EJECUTADO - REVISAR RESULTADOS")
            print(f"="*60)
            
    except Exception as e:
        print(f"Error: {e}")