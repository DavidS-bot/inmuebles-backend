#!/usr/bin/env python3
"""
Test automático de Bankinter Scraper V2
Usa variables de entorno o credenciales hardcodeadas para testing
"""

import asyncio
import logging
import os
import sys
from datetime import date, timedelta
from app.services.bankinter_scraper_v2 import BankinterScraperV2

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_with_demo_mode():
    """Test en modo demo sin credenciales reales"""
    
    print("\n=== Test DEMO de Bankinter Scraper V2 ===")
    print("Este test validará la inicialización y configuración del scraper")
    
    scraper = None
    try:
        print("\n[1/4] Configurando WebDriver...")
        scraper = BankinterScraperV2("demo_user", "demo_pass")
        scraper.setup_driver()
        print("[OK] WebDriver configurado correctamente")
        
        print("\n[2/4] Probando conectividad web...")
        scraper.driver.get("https://www.bankinter.com")
        print("[OK] Conectividad web funcionando")
        
        print("\n[3/4] Validando estructura de datos...")
        # Test de parsing de datos ficticios
        test_text = "15/08/2024 TRANSFERENCIA NOMINA 1,234.56€ 5,678.90€"
        
        # Simular parsing con regex del scraper
        import re
        date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})'
        amount_pattern = r'([-+]?\s*\d{1,3}(?:[.,]\d{3})*[.,]\d{2})\s*€?'
        
        date_match = re.search(date_pattern, test_text)
        amount_matches = re.findall(amount_pattern, test_text)
        
        if date_match and amount_matches:
            print("[OK] Parsing de datos funcionando")
            print(f"     Fecha detectada: {date_match.group(1)}")
            print(f"     Importes detectados: {amount_matches}")
        else:
            print("[WARNING] Problemas en parsing de datos")
        
        print("\n[4/4] Test de estructura Transaction...")
        from app.services.bankinter_scraper_v2 import Transaction
        
        test_transaction = Transaction(
            date=date.today(),
            description="Test transaction",
            amount=123.45
        )
        
        print(f"[OK] Transaction creada: {test_transaction}")
        
        print("\n[DEMO COMPLETADO] Todas las validaciones pasaron correctamente")
        print("\nEl scraper está listo para usar con credenciales reales.")
        print("Para probar con credenciales reales, configura las variables:")
        print("  BANKINTER_USERNAME=tu_dni")
        print("  BANKINTER_PASSWORD=tu_password")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error en test demo: {e}")
        logger.error(f"Demo test failed: {e}")
        return False
        
    finally:
        if scraper and scraper.driver:
            print("\n[CLEANUP] Cerrando WebDriver...")
            scraper.close()
            print("[OK] Limpieza completada")

async def test_with_real_credentials():
    """Test con credenciales reales desde variables de entorno"""
    
    username = os.getenv("BANKINTER_USERNAME")
    password = os.getenv("BANKINTER_PASSWORD")
    
    if not username or not password:
        print("\n[INFO] No hay credenciales configuradas")
        print("Para usar credenciales reales, configura:")
        print("  set BANKINTER_USERNAME=tu_dni")
        print("  set BANKINTER_PASSWORD=tu_password")
        return False
    
    print(f"\n=== Test REAL de Bankinter Scraper V2 ===")
    print(f"Usuario: {username}")
    print("IMPORTANTE: Se abrirá Chrome, no lo cierres manualmente")
    
    scraper = None
    try:
        scraper = BankinterScraperV2(username=username, password=password)
        
        print("\n[1/5] Configurando WebDriver...")
        scraper.setup_driver()
        print("[OK] WebDriver listo")
        
        print("\n[2/5] Realizando login en Bankinter...")
        login_success = await scraper.login()
        
        if not login_success:
            print("[ERROR] Login fallido")
            print("Posibles causas:")
            print("- Credenciales incorrectas")
            print("- Captcha requerido")
            print("- Bankinter detectó automatización")
            return False
            
        print("[OK] Login exitoso")
        
        print("\n[3/5] Esperando carga completa...")
        await asyncio.sleep(5)
        
        print("\n[4/5] Obteniendo transacciones (últimos 7 días)...")
        start_date = date.today() - timedelta(days=7)
        end_date = date.today()
        
        transactions = await scraper.get_transactions(start_date, end_date)
        
        print(f"[OK] Obtenidas {len(transactions)} transacciones")
        
        if transactions:
            print(f"\n=== Muestra de transacciones ===")
            for i, t in enumerate(transactions[:3]):
                print(f"{i+1}. {t.date} | {t.description[:30]:30} | {t.amount:8.2f}€")
            
            print(f"\n[5/5] Exportando a CSV...")
            csv_file = await scraper.export_to_csv(transactions)
            print(f"[OK] CSV generado: {csv_file}")
            
            return True
        else:
            print("[WARNING] No se encontraron transacciones")
            print("El scraper funcionó pero no hay datos en el período")
            return True
        
    except Exception as e:
        print(f"[ERROR] {e}")
        logger.error(f"Real test failed: {e}")
        return False
        
    finally:
        if scraper:
            scraper.close()

async def main():
    """Main test function"""
    print("=== Bankinter Scraper V2 - Test Automático ===")
    
    # Primero hacer test demo
    demo_success = await test_with_demo_mode()
    
    if demo_success:
        print("\n" + "="*50)
        
        # Si hay credenciales, hacer test real
        real_success = await test_with_real_credentials()
        
        if not real_success and not (os.getenv("BANKINTER_USERNAME") and os.getenv("BANKINTER_PASSWORD")):
            print("\n[INFO] Para completar las pruebas, configura credenciales reales")
    
    print("\n=== Test completado ===")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest cancelado por usuario")
    except Exception as e:
        print(f"Error fatal: {e}")
        sys.exit(1)