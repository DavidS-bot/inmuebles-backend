#!/usr/bin/env python3
"""
Test del mes actual - Agosto 2025
"""

import asyncio
import logging
from datetime import date, datetime, timedelta
from app.services.bankinter_scraper_v2 import BankinterScraperV2

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_mes_actual():
    """Probar scraping del mes actual"""
    
    # Credenciales
    username = "75867185"
    password = "Motoreta123$"
    
    # Rango del mes actual (agosto 2025)
    today = date.today()
    start_date = date(today.year, today.month, 1)  # Primer día del mes
    end_date = today  # Hasta hoy
    
    print(f"\n=== Test Mes Actual - {today.strftime('%B %Y')} ===")
    print(f"Usuario: {username}")
    print(f"Período: {start_date} a {end_date} ({(end_date - start_date).days + 1} días)")
    
    scraper = None
    try:
        scraper = BankinterScraperV2(username=username, password=password)
        
        print("\n[1/6] Configurando WebDriver...")
        scraper.setup_driver()
        print("[OK] WebDriver listo")
        
        print("\n[2/6] Realizando login...")
        login_success = await scraper.login()
        
        if not login_success:
            print("[ERROR] Login fallido")
            return
            
        print("[OK] Login exitoso")
        
        print("\n[3/6] Esperando carga completa...")
        await asyncio.sleep(5)
        
        print("\n[4/6] Obteniendo transacciones del mes actual...")
        transactions = await scraper.get_transactions(start_date, end_date)
        
        print(f"\n[5/6] RESULTADO:")
        print(f"Transacciones encontradas: {len(transactions)}")
        
        if transactions:
            print(f"\n=== MOVIMIENTOS DE {start_date.strftime('%B %Y').upper()} ===")
            
            # Mostrar todas las transacciones encontradas
            for i, t in enumerate(transactions, 1):
                fecha_str = t.date.strftime('%d/%m/%Y')
                print(f"{i:2d}. {fecha_str} | {t.description[:60]:60} | {t.amount:10.2f}€")
            
            # Resumen financiero
            ingresos = sum(t.amount for t in transactions if t.amount > 0)
            gastos = sum(t.amount for t in transactions if t.amount < 0)
            neto = ingresos + gastos
            
            print(f"\n=== RESUMEN FINANCIERO ===")
            print(f"Total ingresos:  {ingresos:10.2f}€")
            print(f"Total gastos:    {gastos:10.2f}€")
            print(f"Balance neto:    {neto:10.2f}€")
            
            # Análisis por tipo
            print(f"\n=== ANÁLISIS ===")
            print(f"Movimientos positivos: {len([t for t in transactions if t.amount > 0])}")
            print(f"Movimientos negativos: {len([t for t in transactions if t.amount < 0])}")
            print(f"Movimiento promedio:   {sum(t.amount for t in transactions) / len(transactions):10.2f}€")
            
            # Exportar a CSV
            print(f"\n[6/6] Exportando datos...")
            csv_file = await scraper.export_to_csv(
                transactions, 
                f"movimientos_agosto_2025_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            print(f"[OK] Exportado a: {csv_file}")
            
        else:
            print(f"\n⚠️ No se encontraron transacciones en el período")
            print(f"Posibles causas:")
            print(f"- No hay movimientos en agosto 2025")
            print(f"- El scraper necesita navegar a otra página")
            print(f"- Los datos están en un formato diferente")
            
            # Información adicional para debug
            print(f"\n=== DEBUG INFO ===")
            try:
                current_url = scraper.driver.current_url
                print(f"URL actual: {current_url}")
                
                # Buscar texto que indique información financiera
                page_source = scraper.driver.page_source.lower()
                financial_keywords = ['saldo', 'balance', 'movimiento', 'transacción', 'operación', '€', 'eur']
                
                found_keywords = [kw for kw in financial_keywords if kw in page_source]
                print(f"Palabras clave encontradas: {found_keywords}")
                
                if '€' in page_source or 'eur' in page_source:
                    print("✓ La página contiene información monetaria")
                else:
                    print("✗ No se detectó información monetaria")
                    
            except Exception as e:
                print(f"Error en debug: {e}")
        
        return len(transactions) > 0
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        logger.error(f"Test falló: {e}")
        return False
        
    finally:
        if scraper:
            print("\n[LIMPIEZA] Cerrando navegador...")
            scraper.close()
            print("[OK] Test completado")

if __name__ == "__main__":
    try:
        result = asyncio.run(test_mes_actual())
        if result:
            print(f"\n✅ Test exitoso - Se encontraron movimientos")
        else:
            print(f"\n⚠️ Test completado pero sin movimientos")
    except KeyboardInterrupt:
        print(f"\n🛑 Test cancelado por usuario")
    except Exception as e:
        print(f"\n💥 Error fatal: {e}")