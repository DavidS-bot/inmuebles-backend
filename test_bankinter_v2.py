#!/usr/bin/env python3
"""
Script de prueba para Bankinter Scraper V2
"""

import asyncio
import logging
import os
from datetime import date, timedelta
from app.services.bankinter_scraper_v2 import BankinterScraperV2

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bankinter_test.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def test_bankinter_scraper():
    """Probar el scraper v2 de Bankinter"""
    
    # Obtener credenciales de variables de entorno o input
    username = os.getenv("BANKINTER_USERNAME")
    password = os.getenv("BANKINTER_PASSWORD")
    
    if not username or not password:
        print("\n=== Credenciales de Bankinter ===")
        username = input("Usuario DNI: ")
        password = input("Contraseña: ")
    
    print(f"\n=== Iniciando prueba del scraper v2 ===")
    print(f"Usuario: {username}")
    print(f"Fecha: {date.today()}")
    
    scraper = None
    try:
        # Crear scraper
        scraper = BankinterScraperV2(username=username, password=password)
        
        # Test 1: Setup del WebDriver
        print("\n1. Configurando WebDriver...")
        scraper.setup_driver()
        print("✅ WebDriver configurado correctamente")
        
        # Test 2: Login
        print("\n2. Realizando login...")
        login_success = await scraper.login()
        
        if not login_success:
            print("❌ Login fallido")
            return
            
        print("✅ Login exitoso")
        
        # Test 3: Obtener transacciones de los últimos 7 días
        print("\n3. Obteniendo transacciones de los últimos 7 días...")
        start_date = date.today() - timedelta(days=7)
        end_date = date.today()
        
        transactions = await scraper.get_transactions(start_date, end_date)
        
        print(f"✅ Obtenidas {len(transactions)} transacciones")
        
        # Mostrar algunas transacciones de ejemplo
        if transactions:
            print("\n=== Primeras 3 transacciones ===")
            for i, t in enumerate(transactions[:3]):
                print(f"{i+1}. {t.date} - {t.description[:50]} - {t.amount:.2f}€")
        
        # Test 4: Exportar a CSV
        if transactions:
            print("\n4. Exportando a CSV...")
            csv_file = await scraper.export_to_csv(transactions)
            print(f"✅ Exportado a: {csv_file}")
        
        # Test 5: Verificar datos
        print("\n=== Resumen de validación ===")
        print(f"Total transacciones: {len(transactions)}")
        
        if transactions:
            total_amount = sum(t.amount for t in transactions)
            print(f"Importe total: {total_amount:.2f}€")
            
            dates = [t.date for t in transactions]
            print(f"Rango fechas: {min(dates)} - {max(dates)}")
            
            # Verificar que las fechas están en el rango esperado
            valid_dates = all(start_date <= t.date <= end_date for t in transactions)
            print(f"Fechas válidas: {'✅' if valid_dates else '❌'}")
            
            # Verificar que hay descripciones
            valid_descriptions = all(len(t.description.strip()) > 3 for t in transactions)
            print(f"Descripciones válidas: {'✅' if valid_descriptions else '❌'}")
            
            # Verificar que hay importes
            valid_amounts = all(t.amount != 0 for t in transactions)
            print(f"Importes válidos: {'✅' if valid_amounts else '❌'}")
        
        print("\n🎉 Prueba completada exitosamente")
        
    except Exception as e:
        logger.error(f"Error durante la prueba: {e}")
        print(f"❌ Error: {e}")
        
    finally:
        if scraper:
            scraper.close()
            print("\n🔒 WebDriver cerrado")

async def test_quick_validation():
    """Prueba rápida solo para validar que el scraper puede inicializar"""
    print("\n=== Prueba rápida de validación ===")
    
    try:
        scraper = BankinterScraperV2("test_user", "test_pass")
        scraper.setup_driver()
        
        # Solo ir a la página principal para verificar conectividad
        scraper.driver.get("https://www.bankinter.com")
        
        print("[OK] Conectividad web OK")
        print("[OK] WebDriver funcionando")
        
        scraper.close()
        print("[OK] Scraper inicializado correctamente")
        
    except Exception as e:
        print(f"[ERROR] Error en validacion rapida: {e}")

def main():
    """Menu principal"""
    print("=== Test Bankinter Scraper V2 ===")
    print("Ejecutando validación rápida...")
    
    # Por defecto ejecutar validación rápida
    asyncio.run(test_quick_validation())

if __name__ == "__main__":
    main()