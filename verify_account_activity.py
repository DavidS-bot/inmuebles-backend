#!/usr/bin/env python3
"""
Verificar actividad bancaria real en diferentes períodos
"""

import asyncio
from datetime import date
from app.services.bankinter_scraper_v2 import BankinterScraperV2

async def verify_account():
    """Verificar movimientos en diferentes períodos"""
    
    username = "75867185"
    password = "Motoreta123$"
    
    print("VERIFICACION DE ACTIVIDAD BANCARIA REAL")
    print("=" * 50)
    
    # Períodos a verificar
    periodos = [
        ("Julio 2025", date(2025, 7, 1), date(2025, 7, 31)),
        ("Junio 2025", date(2025, 6, 1), date(2025, 6, 30)),
        ("Mayo 2025", date(2025, 5, 1), date(2025, 5, 31)),
        ("2024 Completo", date(2024, 1, 1), date(2024, 12, 31)),
        ("2023 Completo", date(2023, 1, 1), date(2023, 12, 31))
    ]
    
    scraper = None
    try:
        scraper = BankinterScraperV2(username=username, password=password)
        scraper.setup_driver()
        
        print("Realizando login...")
        if not await scraper.login():
            print("ERROR: Login fallido")
            return
        
        print("✅ Login exitoso\n")
        
        for nombre, start_date, end_date in periodos:
            print(f"Verificando {nombre} ({start_date} - {end_date})...")
            
            try:
                transactions = await scraper.get_transactions(start_date, end_date)
                
                if transactions:
                    print(f"  ✅ {len(transactions)} movimientos encontrados")
                    
                    # Mostrar algunos ejemplos
                    print(f"  Ejemplos:")
                    for i, t in enumerate(transactions[:3]):
                        fecha = t.date.strftime('%d/%m/%Y')
                        desc = t.description[:40] if len(t.description) > 40 else t.description
                        print(f"    {i+1}. {fecha} - {desc} - {t.amount:.2f}EUR")
                    
                    if len(transactions) > 3:
                        print(f"    ... y {len(transactions) - 3} movimientos más")
                    
                    # Si encontramos datos, exportar y terminar
                    print(f"\n🎯 ¡DATOS REALES ENCONTRADOS EN {nombre}!")
                    csv_file = await scraper.export_to_csv(transactions, f"movimientos_{nombre.lower().replace(' ', '_')}.csv")
                    print(f"   Exportado a: {csv_file}")
                    
                    # Resumen
                    total = sum(t.amount for t in transactions)
                    ingresos = sum(t.amount for t in transactions if t.amount > 0)
                    gastos = sum(t.amount for t in transactions if t.amount < 0)
                    
                    print(f"\n   RESUMEN {nombre}:")
                    print(f"   - Total movimientos: {len(transactions)}")
                    print(f"   - Total ingresos: {ingresos:.2f}EUR")
                    print(f"   - Total gastos: {gastos:.2f}EUR")
                    print(f"   - Balance neto: {total:.2f}EUR")
                    
                    return True
                
                else:
                    print(f"  ❌ Sin movimientos")
                    
            except Exception as e:
                print(f"  ⚠️  Error: {e}")
            
            # Pausa entre consultas
            await asyncio.sleep(2)
        
        print(f"\n❌ No se encontraron movimientos en ningún período")
        print(f"Posibles causas:")
        print(f"- Cuenta nueva sin historial")
        print(f"- Cuenta inactiva")
        print(f"- Los movimientos requieren autenticación adicional")
        
        return False
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False
        
    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    asyncio.run(verify_account())