#!/usr/bin/env python3
"""
Test del flujo completo: Scraping + Generación de archivos listos para subida manual
"""

import asyncio
import logging
from app.services.bankinter_scraper_v7 import BankinterScraperV7

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_complete_flow():
    """Test completo del flujo automatizado"""
    
    print("FLUJO COMPLETO AUTOMATIZADO - BANKINTER -> AGENTE FINANCIERO")
    print("=" * 80)
    print("Este proceso:")
    print("1. Extrae movimientos de Bankinter con importes correctos")
    print("2. Genera archivos Excel listos para el agente financiero") 
    print("3. Crea archivos en formato correcto para subida manual")
    print("=" * 80)
    
    # Credenciales Bankinter
    bankinter_username = "75867185"
    bankinter_password = "Motoreta123$"
    
    print(f"\nUsuario Bankinter: {bankinter_username}")
    print("Generando archivos sin subida automatica...")
    
    scraper = None
    try:
        # Crear scraper SIN subida automática (solo generar archivos)
        scraper = BankinterScraperV7(
            username=bankinter_username, 
            password=bankinter_password,
            auto_upload=False  # Solo generar archivos
        )
        
        print(f"\n[1/4] Configurando navegador...")
        scraper.setup_driver()
        print("OK - Navegador configurado")
        
        print(f"\n[2/4] Realizando login en Bankinter...")
        if not await scraper.login():
            print("ERROR - Login fallido en Bankinter")
            return False
        print("OK - Login exitoso en Bankinter")
        
        print(f"\n[3/4] Navegando a movimientos...")
        if not await scraper.navigate_to_movements():
            print("ERROR - No se pudo navegar a movimientos")
            return False
        print("OK - Página de movimientos cargada")
        
        print(f"\n[4/4] Extrayendo y generando archivos...")
        result = await scraper.get_august_movements_corrected()
        
        if len(result) == 5:
            transactions, excel_display, excel_api, csv_file, upload_result = result
        else:
            print("ERROR - Formato de resultado inesperado")
            return False
        
        if not transactions:
            print("ERROR - No se encontraron movimientos")
            return False
        
        print(f"\n*** PROCESO COMPLETADO ***")
        print(f"Movimientos extraidos: {len(transactions)}")
        print(f"Primer movimiento: {transactions[0].date.strftime('%d/%m/%Y')} - {transactions[0].description[:40]}... - {transactions[0].amount:+.2f}€")
        print(f"Ultimo movimiento: {transactions[-1].date.strftime('%d/%m/%Y')} - {transactions[-1].description[:40]}... - {transactions[-1].amount:+.2f}€")
        
        print(f"\n*** ARCHIVOS GENERADOS ***")
        print(f"1. PARA VISUALIZACION (formato español):")
        print(f"   {excel_display}")
        print(f"   {csv_file}")
        print(f"\n2. PARA SUBIDA AL AGENTE FINANCIERO:")
        print(f"   {excel_api} <- ¡USAR ESTE ARCHIVO!")
        
        print(f"\n*** SIGUIENTE PASO ***")
        print(f"Ve a: https://inmuebles-david.vercel.app/financial-agent/movements")
        print(f"Sube manualmente el archivo: {excel_api}")
        print(f"Este archivo tiene formato correcto (750.00) para la API")
        print(f"Los {len(transactions)} movimientos apareceran en la interfaz")
        
        # Mostrar preview de algunos movimientos
        print(f"\n*** PREVIEW DE MOVIMIENTOS ***")
        print(f"{'Fecha':<12} {'Concepto':<40} {'Importe':<12}")
        print("-" * 64)
        for i, t in enumerate(transactions[:10]):
            fecha = t.date.strftime('%d/%m/%Y')
            concepto = t.description[:37] + "..." if len(t.description) > 40 else t.description
            importe = f"{t.amount:+8.2f}€"
            print(f"{fecha:<12} {concepto:<40} {importe:<12}")
        
        if len(transactions) > 10:
            print(f"... y {len(transactions) - 10} movimientos más")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    resultado = asyncio.run(test_complete_flow())
    
    if resultado:
        print(f"\n" + "="*80)
        print(f"EXITO - ARCHIVOS LISTOS PARA SUBIDA MANUAL")
        print(f"="*80)
        print(f"Los archivos Excel están listos con formato correcto.")
        print(f"Sube manualmente a: https://inmuebles-david.vercel.app/financial-agent/movements")
    else:
        print(f"\n❌ PROCESO COMPLETADO CON INCIDENCIAS")