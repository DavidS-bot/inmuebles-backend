#!/usr/bin/env python3
"""
Script de prueba real para Bankinter Scraper V2
"""

import asyncio
import logging
import sys
from datetime import date, timedelta
from app.services.bankinter_scraper_v2 import BankinterScraperV2

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_real_scraping():
    """Probar scraping real con credenciales"""
    
    print("\n=== Test REAL de Bankinter Scraper V2 ===")
    
    # Pedir credenciales
    print("\nIntroduce tus credenciales de Bankinter:")
    username = input("DNI/NIE: ")
    if not username:
        print("DNI requerido")
        return
        
    password = input("Password: ")
    if not password:
        print("Password requerido") 
        return
    
    print(f"\nIniciando scraping para usuario: {username}")
    print("NOTA: Se abrira una ventana de Chrome, no la cierres manualmente")
    
    scraper = None
    try:
        # Crear scraper
        scraper = BankinterScraperV2(username=username, password=password)
        
        print("\n[1/5] Configurando WebDriver...")
        scraper.setup_driver()
        print("[OK] WebDriver listo")
        
        print("\n[2/5] Realizando login...")
        login_success = await scraper.login()
        
        if not login_success:
            print("[ERROR] Login fallido - verifica credenciales")
            return
            
        print("[OK] Login exitoso")
        
        print("\n[3/5] Esperando a que la pagina cargue completamente...")
        await asyncio.sleep(5)  # Dar tiempo a que cargue todo
        
        print("\n[4/5] Obteniendo transacciones de los ultimos 30 dias...")
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()
        
        transactions = await scraper.get_transactions(start_date, end_date)
        
        print(f"[OK] Obtenidas {len(transactions)} transacciones")
        
        if transactions:
            print(f"\n=== Resumen de transacciones ===")
            print(f"Periodo: {start_date} a {end_date}")
            print(f"Total transacciones: {len(transactions)}")
            
            # Mostrar primeras 5 transacciones
            print(f"\n=== Primeras 5 transacciones ===")
            for i, t in enumerate(transactions[:5]):
                print(f"{i+1}. {t.date} | {t.description[:40]:40} | {t.amount:8.2f}€")
            
            if len(transactions) > 5:
                print(f"... y {len(transactions) - 5} transacciones mas")
            
            # Calcular totales
            ingresos = sum(t.amount for t in transactions if t.amount > 0)
            gastos = sum(t.amount for t in transactions if t.amount < 0)
            neto = ingresos + gastos
            
            print(f"\n=== Resumen financiero ===")
            print(f"Ingresos:  {ingresos:8.2f}€")
            print(f"Gastos:    {gastos:8.2f}€")
            print(f"Neto:      {neto:8.2f}€")
            
            print(f"\n[5/5] Exportando a CSV...")
            csv_file = await scraper.export_to_csv(transactions)
            print(f"[OK] Exportado a: {csv_file}")
            
        else:
            print("[WARNING] No se encontraron transacciones")
            print("Posibles causas:")
            print("- No hay movimientos en el periodo")
            print("- La pagina no cargo correctamente")
            print("- Bankinter cambio su interfaz")
        
        print(f"\n[COMPLETADO] Test finalizado exitosamente")
        
    except KeyboardInterrupt:
        print(f"\n[CANCELADO] Test interrumpido por usuario")
        
    except Exception as e:
        logger.error(f"Error durante el scraping: {e}")
        print(f"[ERROR] {e}")
        
    finally:
        if scraper:
            print("\n[CLEANUP] Cerrando WebDriver...")
            scraper.close()
            print("[OK] Limpieza completada")

if __name__ == "__main__":
    try:
        asyncio.run(test_real_scraping())
    except KeyboardInterrupt:
        print("\nTest cancelado por usuario")
    except Exception as e:
        print(f"Error fatal: {e}")
        sys.exit(1)