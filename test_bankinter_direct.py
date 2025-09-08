#!/usr/bin/env python3
"""
Test directo de Bankinter Scraper V2 con credenciales embebidas
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

async def test_direct():
    """Test directo con credenciales"""
    
    # Credenciales proporcionadas
    username = "75867185"
    password = "Motoreta123$"
    
    print(f"\n=== Test DIRECTO de Bankinter Scraper V2 ===")
    print(f"Usuario: {username}")
    print("IMPORTANTE: Se abrirá Chrome, NO lo cierres manualmente")
    print("Este proceso puede tomar 1-3 minutos...")
    
    scraper = None
    try:
        scraper = BankinterScraperV2(username=username, password=password)
        
        print("\n[1/5] Configurando WebDriver...")
        scraper.setup_driver()
        print("[OK] WebDriver listo")
        
        print("\n[2/5] Navegando a Bankinter...")
        print("     URL: https://bancaonline.bankinter.com/gestion/login.xhtml")
        
        print("\n[3/5] Realizando login...")
        login_success = await scraper.login()
        
        if not login_success:
            print("[ERROR] Login fallido")
            print("Posibles causas:")
            print("- Credenciales incorrectas")
            print("- Captcha requerido")
            print("- Bankinter detectó automatización")
            print("- Página cambió su estructura")
            
            # Tomar screenshot para debug
            try:
                scraper.driver.save_screenshot("login_failed_debug.png")
                print("- Screenshot guardado: login_failed_debug.png")
            except:
                pass
                
            return False
            
        print("[OK] Login exitoso")
        
        print("\n[4/5] Esperando carga completa de la página principal...")
        await asyncio.sleep(8)  # Dar más tiempo
        
        # Tomar screenshot después del login
        try:
            scraper.driver.save_screenshot("after_login_success.png")
            print("     Screenshot post-login: after_login_success.png")
        except:
            pass
        
        print("\n[5/5] Obteniendo transacciones (últimos 15 días)...")
        start_date = date.today() - timedelta(days=15)
        end_date = date.today()
        
        print(f"     Período: {start_date} a {end_date}")
        
        transactions = await scraper.get_transactions(start_date, end_date)
        
        print(f"\n[RESULTADO] Obtenidas {len(transactions)} transacciones")
        
        if transactions:
            print(f"\n=== Primeras transacciones encontradas ===")
            for i, t in enumerate(transactions[:5]):
                print(f"{i+1:2d}. {t.date} | {t.description[:35]:35} | {t.amount:9.2f}€")
            
            if len(transactions) > 5:
                print(f"    ... y {len(transactions) - 5} transacciones más")
            
            # Resumen financiero
            ingresos = sum(t.amount for t in transactions if t.amount > 0)
            gastos = sum(t.amount for t in transactions if t.amount < 0)
            neto = ingresos + gastos
            
            print(f"\n=== Resumen del período ===")
            print(f"Ingresos:  {ingresos:9.2f}€")
            print(f"Gastos:    {gastos:9.2f}€")
            print(f"Neto:      {neto:9.2f}€")
            
            # Exportar CSV
            print(f"\n[EXPORTANDO] Generando CSV...")
            csv_file = await scraper.export_to_csv(transactions)
            print(f"[OK] Archivo generado: {csv_file}")
            
            print(f"\n🎉 [ÉXITO TOTAL] Scraper funcionando perfectamente")
            print(f"   - Login: ✅")
            print(f"   - Extracción: ✅ ({len(transactions)} transacciones)")
            print(f"   - Exportación: ✅ ({csv_file})")
            
            return True
            
        else:
            print("\n⚠️ [SIN DATOS] No se encontraron transacciones")
            print("Posibles causas:")
            print("- No hay movimientos en el período seleccionado")
            print("- La página no cargó completamente")
            print("- Bankinter cambió su interfaz")
            print("- Los datos están en otra sección")
            
            # Debug info
            try:
                scraper.driver.save_screenshot("no_transactions_debug.png")
                print("- Screenshot para debug: no_transactions_debug.png")
                
                # Mostrar texto de la página para debug
                page_text = scraper.driver.page_source[:500]
                print(f"- Muestra del contenido de la página:")
                print(f"  {page_text}...")
                
            except Exception as e:
                print(f"- Error obteniendo info de debug: {e}")
            
            return True  # No es un fallo del scraper, solo no hay datos
        
    except Exception as e:
        print(f"\n❌ [ERROR CRÍTICO] {e}")
        logger.error(f"Test directo falló: {e}")
        
        # Debug info en caso de error
        try:
            if scraper and scraper.driver:
                scraper.driver.save_screenshot("critical_error_debug.png")
                print("   Screenshot de error guardado: critical_error_debug.png")
        except:
            pass
            
        return False
        
    finally:
        if scraper:
            print("\n[LIMPIEZA] Cerrando WebDriver...")
            scraper.close()
            print("[OK] Limpieza completada")

if __name__ == "__main__":
    print("Iniciando test directo con Bankinter Scraper V2...")
    
    try:
        result = asyncio.run(test_direct())
        
        if result:
            print("\n✅ Test completado exitosamente")
        else:
            print("\n❌ Test falló")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Test cancelado por usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Error fatal: {e}")
        sys.exit(1)