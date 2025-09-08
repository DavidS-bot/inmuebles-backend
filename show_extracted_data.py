#!/usr/bin/env python3
"""
Mostrar exactamente qué datos se están extrayendo
"""

import asyncio
import logging
from datetime import date
from app.services.bankinter_scraper_v2 import BankinterScraperV2

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def show_extracted_data():
    """Mostrar datos extraídos sin filtros"""
    
    username = "75867185"
    password = "Motoreta123$"
    
    print(f"\n=== ANALISIS DE DATOS EXTRAIDOS ===")
    print(f"Usuario: {username}")
    
    scraper = None
    try:
        scraper = BankinterScraperV2(username=username, password=password)
        
        print("\n[1/4] Configurando y logueando...")
        scraper.setup_driver()
        
        login_success = await scraper.login()
        if not login_success:
            print("[ERROR] Login fallido")
            return
            
        print("[OK] Login exitoso")
        
        print("\n[2/4] Navegando al area bancaria...")
        await asyncio.sleep(5)
        
        print("\n[3/4] Extrayendo TODOS los datos encontrados...")
        
        # Llamar directamente al método de extracción sin filtros
        all_transactions = scraper._extract_transactions_from_current_page()
        
        print(f"\n[4/4] RESULTADO COMPLETO:")
        print(f"Total elementos encontrados: {len(all_transactions)}")
        
        if all_transactions:
            print(f"\n=== TODOS LOS DATOS EXTRAIDOS ===")
            for i, t in enumerate(all_transactions, 1):
                print(f"\n--- ELEMENTO {i} ---")
                print(f"Fecha: {t.date}")
                print(f"Descripcion: '{t.description}'")
                print(f"Importe: {t.amount}")
                if t.balance:
                    print(f"Saldo: {t.balance}")
                if t.reference:
                    print(f"Referencia: {t.reference}")
        else:
            print(f"\n[INFO] No se extrajo ningun dato")
        
        # Información adicional de debug
        print(f"\n=== INFO DE DEBUG ===")
        current_url = scraper.driver.current_url
        print(f"URL actual: {current_url}")
        
        # Mostrar fragmentos del HTML que contienen números y €
        print(f"\n=== FRAGMENTOS CON INFORMACION FINANCIERA ===")
        page_source = scraper.driver.page_source
        
        # Buscar líneas que contengan € o números
        lines_with_money = []
        for line in page_source.split('\n'):
            line_clean = line.strip()
            if ('€' in line_clean or 'EUR' in line_clean or 
                (',' in line_clean and any(c.isdigit() for c in line_clean))):
                if len(line_clean) > 5 and len(line_clean) < 200:  # Filtrar líneas muy cortas o muy largas
                    lines_with_money.append(line_clean)
        
        # Mostrar las primeras 10 líneas con información financiera
        for i, line in enumerate(lines_with_money[:10], 1):
            print(f"{i:2d}. {line}")
            
        if len(lines_with_money) > 10:
            print(f"... y {len(lines_with_money) - 10} líneas más con información financiera")
            
        print(f"\nTotal líneas con información financiera: {len(lines_with_money)}")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        logger.error(f"Error: {e}")
        
    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    try:
        asyncio.run(show_extracted_data())
    except KeyboardInterrupt:
        print(f"\nCancelado por usuario")
    except Exception as e:
        print(f"Error fatal: {e}")