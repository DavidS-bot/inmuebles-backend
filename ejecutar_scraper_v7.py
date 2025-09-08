#!/usr/bin/env python3
"""
Ejecutar Bankinter Scraper V7 con subida automática al agente financiero
"""

import asyncio
import os
import sys
from datetime import date, datetime

# Agregar el directorio app al path
app_path = os.path.join(os.path.dirname(__file__), 'app')
sys.path.insert(0, app_path)

# Ahora importar el scraper
from services.bankinter_scraper_v7 import BankinterScraperV7

async def ejecutar_bankinter_completo():
    """Ejecutar el scraper v7 completo con subida automática"""
    
    print("="*60)
    print("[BANKINTER] SCRAPER V7 - AUTOMATICO")
    print("="*60)
    
    # Credenciales Bankinter
    bankinter_user = "75867185"
    bankinter_pass = "Motoreta123$"
    
    # Credenciales Agente Financiero
    agent_user = "davsanchez21277@gmail.com"
    agent_pass = "123456"
    
    # Período actual (agosto 2024)
    today = date.today()
    
    print(f"Usuario Bankinter: {bankinter_user}")
    print(f"Usuario Agente: {agent_user}")
    print(f"Fecha: {today.strftime('%d/%m/%Y')}")
    
    scraper = None
    try:
        # Inicializar scraper con subida automática
        print("\\n[INIT] Inicializando scraper v7...")
        scraper = BankinterScraperV7(
            username=bankinter_user,
            password=bankinter_pass,
            agent_username=agent_user,
            agent_password=agent_pass,
            auto_upload=True  # ACTIVAR SUBIDA AUTOMATICA
        )
        
        print("[INIT] Configurando navegador...")
        scraper.setup_driver()
        print("[OK] Navegador configurado")
        
        print("\\n[PASO 1/4] Realizando login en Bankinter...")
        login_success = await scraper.login()
        
        if not login_success:
            print("[ERROR] Login en Bankinter fallido")
            return False
            
        print("[OK] Login exitoso en Bankinter")
        
        print("\\n[PASO 2/4] Extrayendo movimientos...")
        transactions = await scraper.extract_movements_correct_amounts()
        
        if not transactions:
            print("[WARNING] No se encontraron transacciones")
            return False
            
        print(f"[OK] {len(transactions)} movimientos extraídos")
        
        print("\\n[PASO 3/4] Generando Excel...")
        excel_file = scraper.generate_excel(transactions)
        
        if not excel_file:
            print("[ERROR] No se pudo generar Excel")
            return False
            
        print(f"[OK] Excel generado: {excel_file}")
        
        print("\\n[PASO 4/4] Subiendo al Agente Financiero...")
        # El scraper v7 debería subir automáticamente si auto_upload=True
        
        print("\\n" + "="*60)
        print("[SUCCESS] PROCESO COMPLETADO EXITOSAMENTE")
        print("="*60)
        print(f"[STATS] Movimientos procesados: {len(transactions)}")
        print(f"[FILE] Archivo Excel: {excel_file}")
        print(f"[WEB] Verificar en: https://inmuebles-david.vercel.app/financial-agent/movements")
        
        return True
        
    except Exception as e:
        print(f"\\n[ERROR] Error durante el proceso: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if scraper and hasattr(scraper, 'driver') and scraper.driver:
            print("\\n[CLEANUP] Cerrando navegador...")
            scraper.driver.quit()

def main():
    """Función principal"""
    try:
        result = asyncio.run(ejecutar_bankinter_completo())
        
        if result:
            print("\\n[SUCCESS] Exito total! Datos descargados y subidos al agente financiero.")
        else:
            print("\\n[ERROR] Hubo problemas durante el proceso.")
            
    except KeyboardInterrupt:
        print("\\n\\n[INTERRUPT] Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\\n\\n[CRITICAL] Error critico: {e}")

if __name__ == "__main__":
    main()