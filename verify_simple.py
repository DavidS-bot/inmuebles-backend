#!/usr/bin/env python3
"""
Verificar actividad bancaria simple sin emojis
"""

import asyncio
from datetime import date
from app.services.bankinter_scraper_v2 import BankinterScraperV2

async def verify_simple():
    """Verificar movimientos en diferentes períodos"""
    
    username = "75867185"
    password = "Motoreta123$"
    
    print("VERIFICACION DE ACTIVIDAD BANCARIA REAL")
    print("=" * 50)
    
    # Períodos más amplios
    periodos = [
        ("Ultimos 6 meses", date(2025, 2, 1), date(2025, 8, 31)),
        ("Ano 2024", date(2024, 1, 1), date(2024, 12, 31)),
        ("Ano 2023", date(2023, 1, 1), date(2023, 12, 31)),
        ("Todo el historial", date(2020, 1, 1), date(2025, 12, 31))
    ]
    
    scraper = None
    try:
        scraper = BankinterScraperV2(username=username, password=password)
        scraper.setup_driver()
        
        print("Realizando login...")
        if not await scraper.login():
            print("ERROR: Login fallido")
            return
        
        print("OK - Login exitoso")
        
        for nombre, start_date, end_date in periodos:
            print(f"\nVerificando {nombre}...")
            print(f"Periodo: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}")
            
            try:
                transactions = await scraper.get_transactions(start_date, end_date)
                
                if transactions:
                    print(f"ENCONTRADOS: {len(transactions)} movimientos")
                    
                    # Agrupar por mes
                    by_month = {}
                    for t in transactions:
                        month_key = f"{t.date.year}-{t.date.month:02d}"
                        if month_key not in by_month:
                            by_month[month_key] = []
                        by_month[month_key].append(t)
                    
                    print(f"Distribucion por mes:")
                    for month, movs in sorted(by_month.items()):
                        total = sum(m.amount for m in movs)
                        print(f"  {month}: {len(movs):2d} movimientos, {total:8.2f}EUR")
                    
                    # Mostrar algunos movimientos recientes
                    print(f"\nMovimientos mas recientes:")
                    recent = sorted(transactions, key=lambda x: x.date, reverse=True)[:5]
                    for i, t in enumerate(recent, 1):
                        fecha = t.date.strftime('%d/%m/%Y')
                        desc = t.description[:40]
                        print(f"  {i}. {fecha} - {desc} - {t.amount:.2f}EUR")
                    
                    # Exportar
                    csv_name = f"movimientos_reales_{nombre.lower().replace(' ', '_')}.csv"
                    try:
                        csv_file = await scraper.export_to_csv(transactions, csv_name)
                        print(f"\nExportado a: {csv_file}")
                    except Exception as e:
                        print(f"Error exportando: {e}")
                    
                    # Resumen final
                    total_amount = sum(t.amount for t in transactions)
                    ingresos = sum(t.amount for t in transactions if t.amount > 0)
                    gastos = sum(t.amount for t in transactions if t.amount < 0)
                    
                    print(f"\nRESUMEN FINAL:")
                    print(f"- Movimientos totales: {len(transactions)}")
                    print(f"- Ingresos: {ingresos:.2f}EUR")
                    print(f"- Gastos: {gastos:.2f}EUR") 
                    print(f"- Balance: {total_amount:.2f}EUR")
                    
                    print(f"\n" + "="*50)
                    print(f"EXITO: DATOS BANCARIOS REALES ENCONTRADOS")
                    print(f"Scraper funcionando correctamente")
                    print(f"="*50)
                    
                    return True
                
                else:
                    print(f"Sin movimientos en este periodo")
                    
            except Exception as e:
                print(f"Error: {e}")
                continue
        
        print(f"\nNo se encontraron movimientos en ningun periodo")
        print(f"La cuenta puede estar vacia o ser muy nueva")
        
        return False
        
    except Exception as e:
        print(f"ERROR GENERAL: {e}")
        return False
        
    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    asyncio.run(verify_simple())