#!/usr/bin/env python3
"""
Test rápido para generar archivo Excel con formato API (puntos decimales)
"""

import asyncio
from app.services.bankinter_scraper_v7 import BankinterScraperV7
from app.services.financial_agent_uploader import upload_bankinter_excel

async def test_api_format():
    """Test generación de archivo con formato API"""
    
    print("TEST - GENERACIÓN DE ARCHIVO CON FORMATO API")
    print("=" * 60)
    
    # Crear scraper sin subida automática para generar solo archivos
    scraper = BankinterScraperV7(
        username="75867185", 
        password="Motoreta123$",
        auto_upload=False  # Solo generar archivos
    )
    
    try:
        print("Configurando navegador...")
        scraper.setup_driver()
        
        print("Realizando login...")
        if not await scraper.login():
            print("ERROR: Login fallido")
            return False
        
        print("Navegando a movimientos...")
        if not await scraper.navigate_to_movements():
            print("ERROR: No se pudo navegar")
            return False
        
        print("Generando archivos...")
        result = await scraper.get_august_movements_corrected()
        
        if len(result) == 5:  # Nueva estructura con 5 elementos
            transactions, excel_display, excel_api, csv_file, upload_result = result
        else:  # Estructura antigua
            print("Estructura de resultado inesperada")
            return False
        
        if not transactions:
            print("ERROR: No se encontraron transacciones")
            return False
        
        print(f"\n✓ ARCHIVOS GENERADOS:")
        print(f"  - Excel visualización: {excel_display} (formato español: 750,00)")
        print(f"  - Excel para API: {excel_api} (formato americano: 750.00)")
        print(f"  - CSV: {csv_file}")
        print(f"  - Transacciones: {len(transactions)}")
        
        # Test de subida con archivo API
        print(f"\n=== TEST DE SUBIDA CON ARCHIVO API ===")
        
        upload_result = await upload_bankinter_excel(
            excel_file_path=excel_api,  # Usar archivo API
            username="admin",
            password="admin123",
            base_url="http://localhost:8000"
        )
        
        print(f"✓ SUBIDA EXITOSA:")
        print(f"  - Movimientos nuevos: {upload_result['new_movements_created']}")
        print(f"  - Duplicados omitidos: {upload_result['duplicates_skipped']}")
        print(f"  - Total procesados: {upload_result['total_rows_processed']}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        scraper.close()

if __name__ == "__main__":
    resultado = asyncio.run(test_api_format())
    
    if resultado:
        print(f"\n✓ PROCESO COMPLETADO EXITOSAMENTE")
        print("Archivos generados con formato correcto para API")
    else:
        print(f"\n❌ PROCESO FALLÓ")