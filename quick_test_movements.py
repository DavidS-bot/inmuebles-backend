#!/usr/bin/env python3
"""
Test rápido para mostrar exactamente los movimientos encontrados
Usando el scraper V2 que ya funciona
"""

import asyncio
import logging
from datetime import date, datetime
from app.services.bankinter_scraper_v2 import BankinterScraperV2

logging.basicConfig(level=logging.INFO)

async def quick_test():
    """Test rápido para mostrar movimientos"""
    
    username = "75867185"
    password = "Motoreta123$"
    
    # Período completo del año para capturar cualquier dato
    start_date = date(2024, 1, 1)  # Desde enero 2024
    end_date = date(2025, 12, 31)  # Hasta diciembre 2025
    
    print("QUICK TEST - MOVIMIENTOS BANKINTER")
    print("=" * 50)
    print(f"Usuario: {username}")
    print(f"Periodo AMPLIO: {start_date} a {end_date}")
    print("(Para capturar cualquier movimiento que exista)")
    
    scraper = None
    try:
        scraper = BankinterScraperV2(username=username, password=password)
        
        print("\n[1] Configurando y logueando...")
        scraper.setup_driver()
        
        login_ok = await scraper.login()
        if not login_ok:
            print("[ERROR] Login fallido")
            return
        
        print("[OK] Login exitoso")
        
        print("\n[2] Obteniendo TODOS los movimientos posibles...")
        transactions = await scraper.get_transactions(start_date, end_date)
        
        print(f"\n[3] RESULTADO:")
        print(f"Movimientos encontrados: {len(transactions)}")
        
        if transactions:
            print(f"\n=== TODOS LOS MOVIMIENTOS ENCONTRADOS ===")
            
            # Agrupar por mes para mejor visualización
            monthly_data = {}
            for t in transactions:
                month_key = f"{t.date.year}-{t.date.month:02d}"
                if month_key not in monthly_data:
                    monthly_data[month_key] = []
                monthly_data[month_key].append(t)
            
            for month, month_transactions in sorted(monthly_data.items()):
                print(f"\n--- {month} ---")
                for i, t in enumerate(month_transactions, 1):
                    fecha = t.date.strftime('%d/%m/%Y')
                    descripcion = t.description[:50] if len(t.description) > 50 else t.description
                    print(f"{i:2d}. {fecha} | {descripcion:50} | {t.amount:8.2f}EUR")
            
            # Resumen por mes
            print(f"\n=== RESUMEN POR MES ===")
            for month, month_transactions in sorted(monthly_data.items()):
                total = sum(t.amount for t in month_transactions)
                count = len(month_transactions)
                print(f"{month}: {count:2d} movimientos, total: {total:8.2f}EUR")
            
            # Resumen general
            total_amount = sum(t.amount for t in transactions)
            print(f"\n=== RESUMEN GENERAL ===")
            print(f"Total movimientos: {len(transactions)}")
            print(f"Importe total: {total_amount:.2f}EUR")
            
            # Buscar movimientos de agosto 2025 específicamente
            agosto_2025 = [t for t in transactions if t.date.year == 2025 and t.date.month == 8]
            print(f"\nMovimientos de AGOSTO 2025: {len(agosto_2025)}")
            
            if agosto_2025:
                print("MOVIMIENTOS DE AGOSTO 2025:")
                for i, t in enumerate(agosto_2025, 1):
                    print(f"{i}. {t.date.strftime('%d/%m/%Y')} - {t.description} - {t.amount}EUR")
            
            # Exportar todo
            csv_file = await scraper.export_to_csv(transactions, "todos_los_movimientos.csv")
            print(f"\nTodos los datos exportados a: {csv_file}")
            
        else:
            print("No se encontro ningun movimiento")
            
            # Info de debug
            try:
                url = scraper.driver.current_url
                print(f"URL actual: {url}")
                
                # Buscar cualquier número en la página
                page_text = scraper.driver.page_source
                import re
                
                # Buscar patrones de dinero
                money_patterns = re.findall(r'\d+[.,]\d{2}', page_text)
                if money_patterns:
                    print(f"Patrones de dinero encontrados: {money_patterns[:10]}")
                
                # Buscar fechas
                date_patterns = re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{4}', page_text)
                if date_patterns:
                    print(f"Patrones de fecha encontrados: {date_patterns[:10]}")
                    
            except Exception as e:
                print(f"Error en debug: {e}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        
    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    asyncio.run(quick_test())