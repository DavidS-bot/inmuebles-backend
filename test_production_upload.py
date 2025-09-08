#!/usr/bin/env python3
"""
Test de subida a producción en Vercel
"""

import asyncio
import logging
from app.services.financial_agent_uploader import upload_bankinter_excel

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_production_upload():
    """Test de subida a producción en Vercel"""
    
    print("TEST DE SUBIDA A PRODUCCION - VERCEL")
    print("=" * 60)
    
    # Usar el archivo API más reciente (formato americano para API)
    api_file = "bankinter_api_20250828_112544.xlsx"
    
    # URL de producción
    production_url = "https://inmuebles-david.vercel.app"
    
    # Solicitar credenciales de producción
    print("Necesito las credenciales del agente financiero en producción:")
    agent_username = input("Usuario del agente financiero: ").strip()
    agent_password = input("Contraseña del agente financiero: ").strip()
    
    if not agent_username or not agent_password:
        print("ERROR: Se requieren credenciales válidas")
        return False
    
    try:
        print(f"\nArchivo para subida: {api_file}")
        print(f"Backend producción: {production_url}")
        print(f"Usuario: {agent_username}")
        print(f"Formato: Americano (750.00) para API")
        
        print(f"\n=== SUBIENDO A PRODUCCIÓN ===")
        
        result = await upload_bankinter_excel(
            excel_file_path=api_file,
            username=agent_username, 
            password=agent_password,
            base_url=production_url
        )
        
        print(f"\n*** SUBIDA A PRODUCCIÓN EXITOSA ***")
        print(f"  - Movimientos nuevos creados: {result['new_movements_created']}")
        print(f"  - Duplicados omitidos: {result['duplicates_skipped']}")
        print(f"  - Total filas procesadas: {result['total_rows_processed']}")
        print(f"  - Movimientos existentes: {result['existing_movements_found']}")
        print(f"  - Timestamp: {result['upload_timestamp']}")
        
        print(f"\n🎯 VERIFICAR EN:")
        print(f"https://inmuebles-david.vercel.app/financial-agent/movements")
        print(f"\n¡Los {result['new_movements_created']} nuevos movimientos")
        print(f"de Bankinter deberían aparecer en la interfaz!")
        
        return True
        
    except Exception as e:
        print(f"\nERROR en subida a producción: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    resultado = asyncio.run(test_production_upload())
    
    if resultado:
        print(f"\n✓ INTEGRACION COMPLETA FUNCIONANDO EN PRODUCCION")
        print(f"Los datos de Bankinter están ahora en el agente financiero!")
    else:
        print(f"\n❌ Error en la integración con producción")