#!/usr/bin/env python3
"""
Test simple de subida manual con credenciales fijas
"""

import asyncio
import logging
from app.services.financial_agent_uploader import upload_bankinter_excel

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_upload():
    """Test de subida del archivo corregido existente"""
    
    print("TEST DE SUBIDA AL AGENTE FINANCIERO")
    print("=" * 50)
    
    # Usar el archivo corregido más reciente
    excel_file = "bankinter_corregido_20250828_110803.xlsx"
    
    # Credenciales del agente financiero
    agent_username = "admin"  # Usa las credenciales correctas
    agent_password = "admin123"  # Usa las credenciales correctas
    
    try:
        print(f"Subiendo archivo: {excel_file}")
        print(f"Usuario: {agent_username}")
        
        result = await upload_bankinter_excel(
            excel_file_path=excel_file,
            username=agent_username,
            password=agent_password
        )
        
        print("\n✓ SUBIDA EXITOSA:")
        print(f"  - Movimientos nuevos creados: {result['new_movements_created']}")
        print(f"  - Duplicados omitidos: {result['duplicates_skipped']}")
        print(f"  - Total filas procesadas: {result['total_rows_processed']}")
        print(f"  - Movimientos existentes: {result['existing_movements_found']}")
        print(f"  - Timestamp: {result['upload_timestamp']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR en subida: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    resultado = asyncio.run(test_upload())
    
    if resultado:
        print(f"\n✅ PROCESO COMPLETADO EXITOSAMENTE")
    else:
        print(f"\n❌ PROCESO COMPLETADO CON ERRORES")