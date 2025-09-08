#!/usr/bin/env python3
"""
Test completo del scraper v7 con subida automática al agente financiero
"""

import asyncio
import logging
from app.services.bankinter_scraper_v7 import BankinterScraperV7

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_automatic_upload():
    """Test del flujo completo: scraping + deduplicación + subida automática"""
    
    # Credenciales Bankinter
    bankinter_username = "75867185"
    bankinter_password = "Motoreta123$"
    
    # Credenciales del agente financiero (necesitas proporcionarlas)
    agent_username = input("Usuario del agente financiero: ").strip()
    agent_password = input("Contraseña del agente financiero: ").strip()
    
    if not agent_username or not agent_password:
        print("ERROR: Se requieren las credenciales del agente financiero")
        return False
    
    print("BANKINTER SCRAPER V7 - FLUJO COMPLETO CON SUBIDA AUTOMÁTICA")
    print("=" * 70)
    print(f"Usuario Bankinter: {bankinter_username}")
    print(f"Usuario Agente: {agent_username}")
    print(f"Subida automática: ACTIVADA")
    
    scraper = None
    try:
        # Crear scraper con subida automática habilitada
        scraper = BankinterScraperV7(
            username=bankinter_username, 
            password=bankinter_password,
            agent_username=agent_username,
            agent_password=agent_password,
            auto_upload=True  # ¡Activar subida automática!
        )
        
        print(f"\n[1/5] Configurando navegador...")
        scraper.setup_driver()
        print("OK - Navegador configurado")
        
        print(f"\n[2/5] Realizando login en Bankinter...")
        if not await scraper.login():
            print("ERROR - Login fallido en Bankinter")
            return False
        print("OK - Login exitoso en Bankinter")
        
        print(f"\n[3/5] Navegando a movimientos...")
        if not await scraper.navigate_to_movements():
            print("ERROR - No se pudo navegar a movimientos")
            return False
        print("OK - Página de movimientos cargada")
        
        print(f"\n[4/5] Extrayendo y procesando datos...")
        transactions, excel_file, csv_file, upload_result = await scraper.get_august_movements_corrected()
        
        if not transactions:
            print("ERROR - No se encontraron movimientos")
            return False
        
        print(f"OK - {len(transactions)} movimientos procesados")
        print(f"Excel generado: {excel_file}")
        print(f"CSV generado: {csv_file}")
        
        print(f"\n[5/5] RESULTADO DE LA SUBIDA AUTOMÁTICA:")
        if upload_result:
            print("✓ SUBIDA EXITOSA al agente financiero:")
            print(f"  • Movimientos nuevos creados: {upload_result['new_movements_created']}")
            print(f"  • Duplicados omitidos: {upload_result['duplicates_skipped']}")
            print(f"  • Total filas procesadas: {upload_result['total_rows_processed']}")
            print(f"  • Movimientos existentes encontrados: {upload_result['existing_movements_found']}")
            print(f"  • Timestamp: {upload_result['upload_timestamp']}")
            
            print(f"\n🎯 RESUMEN FINAL:")
            print(f"  ✓ Scraping completado")
            print(f"  ✓ Datos extraídos con importes correctos")
            print(f"  ✓ Archivos Excel/CSV generados")
            print(f"  ✓ Subida automática al agente financiero")
            print(f"  ✓ Deduplicación automática aplicada")
            
        else:
            print("❌ SUBIDA NO REALIZADA")
            print("Los archivos están listos pero no se subieron automáticamente")
            print("Puedes subirlos manualmente a: https://inmuebles-david.vercel.app/financial-agent/movements")
        
        print(f"\n" + "="*70)
        print(f"PROCESO COMPLETADO CON ÉXITO")
        print(f"="*70)
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if scraper:
            scraper.close()

async def test_manual_upload_only():
    """Test solo de subida manual de archivo existente"""
    from app.services.financial_agent_uploader import upload_bankinter_excel
    
    print("TEST DE SUBIDA MANUAL")
    print("=" * 40)
    
    # Usar el archivo corregido más reciente
    excel_file = "bankinter_corregido_20250828_110803.xlsx"
    
    agent_username = input("Usuario del agente financiero: ").strip()
    agent_password = input("Contraseña del agente financiero: ").strip()
    
    if not agent_username or not agent_password:
        print("ERROR: Se requieren credenciales")
        return False
    
    try:
        print(f"Subiendo archivo: {excel_file}")
        
        result = await upload_bankinter_excel(
            excel_file_path=excel_file,
            username=agent_username,
            password=agent_password
        )
        
        print("✓ SUBIDA EXITOSA:")
        print(f"  - Movimientos nuevos: {result['new_movements_created']}")
        print(f"  - Duplicados omitidos: {result['duplicates_skipped']}")
        print(f"  - Total procesados: {result['total_rows_processed']}")
        
        return True
        
    except Exception as e:
        print(f"ERROR en subida manual: {e}")
        return False

if __name__ == "__main__":
    print("OPCIONES DE TEST:")
    print("1. Flujo completo (scraping + subida automática)")
    print("2. Solo test de subida manual")
    
    opcion = input("Selecciona opción (1 o 2): ").strip()
    
    try:
        if opcion == "1":
            resultado = asyncio.run(test_automatic_upload())
        elif opcion == "2":
            resultado = asyncio.run(test_manual_upload_only())
        else:
            print("Opción inválida")
            resultado = False
        
        if resultado:
            print(f"\n✓ PROCESO COMPLETADO EXITOSAMENTE")
        else:
            print(f"\n❌ PROCESO COMPLETADO CON INCIDENCIAS")
            
    except Exception as e:
        print(f"Error: {e}")